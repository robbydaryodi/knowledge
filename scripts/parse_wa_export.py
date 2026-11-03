#!/usr/bin/env python3
"""Ubah ekspor chat WhatsApp (.txt) menjadi JSONL terstruktur + laporan ringkas.

Mengapa skrip, bukan LLM: ekspor chat bisa ribuan baris. Parsing format, penggabungan
pesan multi-baris, masking nomor HP, dan pemetaan pengirim -> peran harus konsisten
dan bisa diulang. LLM dipakai setelahnya, untuk menilai isi pesan yang bertanda 'signals'.

Pemakaian:
  python scripts/parse_wa_export.py raw/chats/grup_pusat.txt \
      --roster config/people.csv --out work/grup_pusat.jsonl \
      --source-name "Koordinasi UKKJ UPT GTK 2026"

Format yang didukung: Android (id/en) "12/10/2026 14.32 - Nama: pesan",
iOS "[12/10/26 14:32:05] Nama: pesan", dengan/tanpa AM/PM. Hanya library standar.
"""
import argparse, csv, hashlib, json, re, sys
from collections import Counter
from datetime import datetime
from pathlib import Path

WS = r'[\s\u202f\u00a0]'
DATE = r'\d{1,2}[/.\-]\d{1,2}[/.\-]\d{2,4}'
TIME = rf'\d{{1,2}}[:.]\d{{2}}(?:[:.]\d{{2}})?(?:{WS}?[APap]\.?[Mm]\.?)?'
IOS = re.compile(rf'^[\u200e\u200f]?\[(?P<d>{DATE}),?{WS}+(?P<t>{TIME})\]{WS}(?P<rest>.*)$')
AND = re.compile(rf'^[\u200e\u200f]?(?P<d>{DATE}),?{WS}+(?P<t>{TIME}){WS}-{WS}(?P<rest>.*)$')
SENDER = re.compile(r'^(?P<s>[^:]{1,60}?):\s(?P<m>.*)$', re.S)

PHONE = re.compile(r'(?<!\d)(?:\+?62|0)[\s-]?8\d{1,3}[\s-]?\d{3,4}[\s-]?\d{2,5}(?!\d)')
PHONE_NAME = re.compile(r'^\+?[\d\s\-]{8,}$')
DELETED = re.compile(r'(pesan ini telah dihapus|you deleted this message|this message was deleted)', re.I)
MEDIA = re.compile(r'^<.*(media|disertakan|omitted).*>$', re.I)
ATTACH = re.compile(r'\((file terlampir|file attached)\)', re.I)

BULAN = r'(?:jan|feb|mar|apr|mei|jun|jul|agu|sep|okt|nov|des)\w*'
SIGNALS = {
    'tenggat': r'\b(paling lambat|batas(?: akhir| waktu)?|deadline|tenggat|sampai dengan|hingga|s\.?d\.?)\b',
    'kewajiban': r'\b(wajib|harus|tidak (?:perlu|boleh|bisa)|boleh|dilarang|diperbolehkan|ditolak|tolak|diusulkan)\b',
    'dokumen': r'(\bsurat\b|\bnomor\b|\bpermen\w*|surat edaran|\bse\b|\bjuknis\b|\blampiran\b|\bpak\b|\bformasi\b|\bsk\b)',
    'tanggal': rf'\b\d{{1,2}}\s{BULAN}\b',
    'tautan': r'(https?://\S+|bit\.ly/\S+|s\.id/\S+)',
}
SIGNALS = {k: re.compile(v, re.I) for k, v in SIGNALS.items()}


def split_date(d):
    a, b, y = re.split(r'[/.\-]', d)
    y = int(y)
    return int(a), int(b), (2000 + y if y < 100 else y)


def parse_time(t):
    t = t.replace('\u202f', ' ').replace('\u00a0', ' ').strip()
    ampm = re.search(r'([AaPp])\.?[Mm]', t)
    core = re.sub(r'\s?[APap]\.?[Mm]\.?', '', t)
    parts = [int(x) for x in re.split(r'[:.]', core)]
    h, m = parts[0], parts[1]
    s = parts[2] if len(parts) > 2 else 0
    if ampm:
        p = ampm.group(1).lower() == 'p'
        h = (h % 12) + (12 if p else 0)
    return h, m, s


def load_roster(path):
    roster = {}
    if not path:
        return roster
    with open(path, newline='', encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            nm = (row.get('nama_di_wa') or '').strip().lower()
            if nm:
                roster[nm] = {'peran': (row.get('peran') or '').strip() or 'TIDAK_DIKENAL',
                              'kategori': (row.get('kategori') or '').strip().lower() or 'tidak_dikenal'}
    return roster


def read_entries(path):
    entries, cur = [], None
    with open(path, encoding='utf-8-sig', errors='replace') as f:
        for ln, line in enumerate(f, 1):
            line = line.rstrip('\n').rstrip('\r')
            m = IOS.match(line) or AND.match(line)
            if m:
                if cur:
                    entries.append(cur)
                cur = {'d': m['d'], 't': m['t'], 'rest': m['rest'], 'line': ln}
            elif cur is not None:
                cur['rest'] += '\n' + line
    if cur:
        entries.append(cur)
    return entries


def detect_dayfirst(entries, default=True):
    firsts = [split_date(e['d'])[0] for e in entries]
    seconds = [split_date(e['d'])[1] for e in entries]
    if firsts and max(firsts) > 12:
        return True
    if seconds and max(seconds) > 12:
        return False
    return default


def display_name(name):
    """Nama pengirim yang berupa nomor HP disamarkan menjadi alias."""
    if PHONE_NAME.match(name):
        return 'KONTAK-' + hashlib.sha1(name.encode()).hexdigest()[:4]
    return name


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('chat')
    ap.add_argument('--out', required=True)
    ap.add_argument('--roster')
    ap.add_argument('--source-name', default=None)
    ap.add_argument('--dayfirst', choices=['auto', 'yes', 'no'], default='auto',
                    help='urutan tanggal; auto = deteksi dari data (hari/bulan bila ambigu)')
    a = ap.parse_args()

    entries = read_entries(a.chat)
    if not entries:
        sys.exit('Tidak ada baris berformat pesan WhatsApp. Cek format ekspor (Android/iOS) dan encoding.')
    dayfirst = {'yes': True, 'no': False}.get(a.dayfirst)
    if dayfirst is None:
        dayfirst = detect_dayfirst(entries)
    roster = load_roster(a.roster)
    src = a.source_name or Path(a.chat).stem

    records, senders, unknown, attachments, bad_dates = [], Counter(), Counter(), [], 0
    for i, e in enumerate(entries, 1):
        x, y, yr = split_date(e['d'])
        day, mon = (x, y) if dayfirst else (y, x)
        try:
            h, mi, s = parse_time(e['t'])
            ts = datetime(yr, mon, day, h, mi, s).isoformat()
        except ValueError:
            ts, bad_dates = None, bad_dates + 1
        sm = SENDER.match(e['rest'])
        if sm:
            sender, text = sm['s'].strip(), sm['m']
            kind = 'pesan'
        else:
            sender, text, kind = None, e['rest'], 'sistem'
        if kind == 'pesan':
            if DELETED.search(text):
                kind = 'dihapus'
            elif MEDIA.match(text.strip()):
                kind = 'media'
            elif ATTACH.search(text):
                kind = 'lampiran'
                attachments.append({'id': f'M{i:05d}', 'ts': ts, 'text': text.strip()[:200]})
        role = cat = None
        shown = None
        if sender:
            info = roster.get(sender.lower())
            if info:
                role, cat = info['peran'], info['kategori']
            else:
                role, cat = 'TIDAK_DIKENAL', 'tidak_dikenal'
                unknown[display_name(sender)] += 1
            senders[sender] += 1
            shown = display_name(sender)
        text = PHONE.sub('[NO_HP]', text)
        sig = [k for k, rx in SIGNALS.items() if rx.search(text)] if kind in ('pesan', 'lampiran') else []
        records.append({'id': f'M{i:05d}', 'source': src, 'ts': ts, 'sender': shown,
                        'sender_role': role, 'sender_category': cat, 'kind': kind,
                        'text': text, 'signals': sig, 'line': e['line']})

    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, 'w', encoding='utf-8') as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')

    stamps = sorted(r['ts'] for r in records if r['ts'])
    flagged = sum(1 for r in records if r['signals'])
    print(f'Sumber        : {src}')
    print(f'Pesan terbaca : {len(records)} (bertanda sinyal: {flagged})')
    print(f'Rentang waktu : {stamps[0][:10] if stamps else "?"} s.d. {stamps[-1][:10] if stamps else "?"}'
          f'  [urutan tanggal: {"hari/bulan" if dayfirst else "bulan/hari"}]')
    if bad_dates:
        print(f'PERINGATAN    : {bad_dates} baris gagal dikonversi tanggalnya')
    print(f'Output        : {a.out}')
    print('\nPengirim teratas:')
    for n, c in senders.most_common(12):
        info = roster.get(n.lower())
        label = f"{info['peran']} / {info['kategori']}" if info else 'BELUM ADA DI ROSTER'
        print(f'  {c:5d}  {display_name(n)}  -> {label}')
    if unknown:
        print(f'\nTINDAK LANJUT: {len(unknown)} pengirim belum ada di roster (dianggap TIDAK_DIKENAL, '
              f'tidak boleh menjadi sumber T2). Tambahkan ke config/people.csv.')
    if attachments:
        print(f'\nLampiran yang dibagikan di chat ({len(attachments)}) - kandidat dasar hukum untuk diunduh:')
        for at in attachments[:15]:
            print(f'  {at["id"]} {(at["ts"] or "")[:10]}  {at["text"]}')


if __name__ == '__main__':
    main()
