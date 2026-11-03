#!/usr/bin/env python3
"""Validasi ledger klaim (ledger/claims.jsonl) terhadap aturan provenance.

Aturan yang ditegakkan (alasannya ada di references/source_tiers.md):
  - setiap klaim punya sumber yang bisa ditelusuri
  - T1 harus dari dokumen resmi (ada file + rujukan pasal/halaman)
  - T2 harus berasal dari pengirim berkategori 'pusat' di roster
  - T4 (inferensi) wajib menyebut klaim dasar (basis) dan tidak boleh berstatus resmi
  - Lapis 1 hanya boleh berisi T1 atau T2
  - T2 yang dibiarkan lama belum dipromosikan/dicabut -> peringatan
  - dua klaim aktif dengan topik sama tetapi isi berbeda -> peringatan konflik

Pemakaian:  python scripts/check_ledger.py ledger/claims.jsonl [--today 2026-10-22]
            [--promote-days 14] [--stale-days 30]
Kode keluar 1 bila ada ERROR.
"""
import argparse, json, sys
from collections import Counter, defaultdict
from datetime import date

REQUIRED = ['id', 'topic', 'statement', 'tier', 'status', 'layer', 'source', 'date_stated', 'date_verified']
TIERS = {'T1', 'T2', 'T3', 'T4'}
STATUS = {'berlaku', 'belum-final', 'dicabut', 'digantikan'}
INACTIVE = {'dicabut', 'digantikan'}


def d(s):
    try:
        return date.fromisoformat(s)
    except (TypeError, ValueError):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('ledger')
    ap.add_argument('--today', default=date.today().isoformat())
    ap.add_argument('--promote-days', type=int, default=14)
    ap.add_argument('--stale-days', type=int, default=30)
    a = ap.parse_args()
    today = d(a.today)

    claims, errors, warns = [], [], []
    with open(a.ledger, encoding='utf-8') as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                claims.append(json.loads(line))
            except json.JSONDecodeError as e:
                errors.append(f'baris {n}: JSON rusak ({e})')

    ids = Counter(c.get('id') for c in claims)
    for k, v in ids.items():
        if v > 1:
            errors.append(f'{k}: id ganda ({v}x)')
    known = set(ids)

    for c in claims:
        cid = c.get('id', '?')
        miss = [k for k in REQUIRED if c.get(k) in (None, '', [])]
        if miss:
            errors.append(f'{cid}: field wajib kosong: {", ".join(miss)}')
            continue
        tier, status, layer = c['tier'], c['status'], c['layer']
        src = c['source'] if isinstance(c['source'], dict) else {}
        if tier not in TIERS:
            errors.append(f'{cid}: tier "{tier}" tidak dikenal')
        if status not in STATUS:
            errors.append(f'{cid}: status "{status}" tidak dikenal (pakai {sorted(STATUS)})')
        if layer not in (1, 2, 3):
            errors.append(f'{cid}: layer harus 1, 2, atau 3')
        for k in ('date_stated', 'date_verified'):
            if d(c.get(k)) is None:
                errors.append(f'{cid}: {k} bukan tanggal ISO (YYYY-MM-DD)')

        if tier == 'T1':
            if src.get('type') != 'regulasi':
                errors.append(f'{cid}: T1 harus bersumber type "regulasi"')
            if not src.get('file') or not src.get('ref'):
                errors.append(f'{cid}: T1 wajib punya source.file dan source.ref (pasal/halaman)')
        elif tier == 'T2':
            if src.get('type') != 'chat':
                errors.append(f'{cid}: T2 harus bersumber type "chat"')
            if src.get('sender_category') != 'pusat':
                errors.append(f'{cid}: T2 hanya untuk pengirim kategori "pusat" '
                              f'(ditemukan: {src.get("sender_category")}). Turunkan ke T3 atau perbaiki roster.')
            if not src.get('ref'):
                errors.append(f'{cid}: T2 wajib punya source.ref (grup, tanggal-jam, id pesan)')
        elif tier == 'T3':
            if src.get('sender_category') == 'pusat':
                warns.append(f'{cid}: T3 tetapi pengirimnya kategori pusat, mungkin seharusnya T2')
            if not src.get('ref'):
                errors.append(f'{cid}: T3 wajib punya source.ref')
        elif tier == 'T4':
            basis = c.get('basis') or []
            if src.get('type') != 'inferensi':
                errors.append(f'{cid}: T4 harus bersumber type "inferensi"')
            if not basis:
                errors.append(f'{cid}: T4 wajib mencantumkan basis (id klaim dasar)')
            for b in basis:
                if b not in known:
                    errors.append(f'{cid}: basis {b} tidak ada di ledger')

        if layer == 1 and tier in ('T3', 'T4'):
            errors.append(f'{cid}: {tier} tidak boleh tampil di Lapis 1 (plafon: Lapis 1 hanya T1/T2)')

        for ref_key in ('supersedes', 'superseded_by'):
            for r in (c.get(ref_key) or []) if isinstance(c.get(ref_key), list) else ([c[ref_key]] if c.get(ref_key) else []):
                if r not in known:
                    errors.append(f'{cid}: {ref_key} menunjuk {r} yang tidak ada')
        if status == 'digantikan' and not c.get('superseded_by'):
            warns.append(f'{cid}: status digantikan tetapi superseded_by kosong')

        stated, verified = d(c.get('date_stated')), d(c.get('date_verified'))
        if status not in INACTIVE and today:
            if tier == 'T2' and stated and (today - stated).days > a.promote_days:
                warns.append(f'{cid}: T2 berumur {(today - stated).days} hari tanpa promosi ke T1. '
                             f'Cari dokumen tertulisnya atau putuskan untuk dicabut.')
            if verified and (today - verified).days > a.stale_days:
                warns.append(f'{cid}: terakhir diverifikasi {(today - verified).days} hari lalu (> {a.stale_days})')
        if c.get('effective_from') and c.get('effective_until'):
            if d(c['effective_from']) and d(c['effective_until']) and d(c['effective_until']) < d(c['effective_from']):
                errors.append(f'{cid}: effective_until lebih awal dari effective_from')

    by_topic = defaultdict(list)
    for c in claims:
        if c.get('status') not in INACTIVE and c.get('topic'):
            by_topic[c['topic']].append(c)
    for topic, cs in by_topic.items():
        if len({(c.get('statement') or '').strip() for c in cs}) > 1:
            detail = '; '.join(f'{c["id"]}[{c.get("tier")}]' for c in cs)
            warns.append(f'KONFLIK topik "{topic}": {detail}. Masukkan ke review_queue, jangan diselesaikan diam-diam.')

    print(f'Klaim: {len(claims)}  |  per tier: ' + ', '.join(f'{t}={sum(1 for c in claims if c.get("tier") == t)}' for t in sorted(TIERS))
          + '  |  per lapis: ' + ', '.join(f'L{l}={sum(1 for c in claims if c.get("layer") == l)}' for l in (1, 2, 3)))
    for e in errors:
        print('[ERROR] ' + e)
    for w in warns:
        print('[PERINGATAN] ' + w)
    print(f'\nERROR: {len(errors)}  PERINGATAN: {len(warns)}')
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
