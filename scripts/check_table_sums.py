#!/usr/bin/env python3
"""Periksa angka total pada tabel markdown: apakah baris TOTAL sama dengan jumlah baris di atasnya,
dan apakah kolom 'Total ...' per baris sama dengan jumlah kolom angka di sebelah kirinya.

Mengapa skrip: angka rekap dari surat resmi sering disalin manual dan LLM bisa meleset saat
menjumlah. Pemeriksaan ini deterministik. Angka format Indonesia (14.863 = empat belas ribu
delapan ratus enam puluh tiga; 84,0 = desimal). Kolom persen dilewati.

Pemakaian:  python scripts/check_table_sums.py output/L3_rujukan.md [file2.md ...]
Kode keluar 1 bila ada ketidakcocokan.
"""
import re, sys
from pathlib import Path


def clean(c):
    return re.sub(r'[*_`]', '', c).strip()


def num(cell):
    c = clean(cell).replace(' ', '')
    if not c or '%' in c:
        return None
    c = c.replace('.', '').replace(',', '.')
    try:
        return float(c)
    except ValueError:
        return None


def is_sep(line):
    return bool(re.match(r'^\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$', line.strip()))


def cells(line):
    s = line.strip()
    if s.startswith('|'):
        s = s[1:]
    if s.endswith('|'):
        s = s[:-1]
    return [c.strip() for c in s.split('|')]


def tables(lines):
    i, heading = 0, ''
    while i < len(lines):
        if lines[i].lstrip().startswith('#'):
            heading = lines[i].strip()
        if lines[i].lstrip().startswith('|') and i + 1 < len(lines) and is_sep(lines[i + 1]):
            start = i
            hdr = cells(lines[i])
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].lstrip().startswith('|'):
                rows.append((j + 1, cells(lines[j])))
                j += 1
            yield heading, hdr, rows
            i = j
        else:
            i += 1


def is_total_row(r):
    return any(re.search(r'\btotal\b', clean(c), re.I) for c in r[:2])


def fmt(x):
    return f'{x:,.0f}'.replace(',', '.') if abs(x - round(x)) < 1e-9 else f'{x:.2f}'


def check(path):
    lines = Path(path).read_text(encoding='utf-8').splitlines()
    problems, checked = [], 0
    for heading, hdr, rows in tables(lines):
        ncol = len(hdr)
        since_total, all_data, subtotals = [], [], []
        for ln, r in rows:
            r = (r + [''] * ncol)[:ncol]
            if is_total_row(r):
                for k in range(ncol):
                    stated = num(r[k])
                    if stated is None or not since_total:
                        continue
                    cands = {
                        'baris sejak total sebelumnya': sum(v[k] for v in since_total if v[k] is not None),
                        'semua baris data': sum(v[k] for v in all_data if v[k] is not None),
                        'semua baris data + subtotal': sum(v[k] for v in all_data + subtotals if v[k] is not None),
                    }
                    checked += 1
                    if not any(abs(stated - c) < 1e-6 for c in cands.values()):
                        main = cands['baris sejak total sebelumnya'] if len(subtotals) == 0 else cands['semua baris data']
                        problems.append((path, ln, heading, clean(hdr[k]), stated, main,
                                         f'baris TOTAL "{clean(r[0]) or clean(r[1])}"'))
                subtotals.append([num(c) for c in r])
                since_total = []
            else:
                vals = [num(c) for c in r]
                since_total.append(vals)
                all_data.append(vals)
        # cek kolom "Total ..." per baris
        tcols = [k for k, h in enumerate(hdr) if re.match(r'^\s*total\b', clean(h), re.I)]
        for k in tcols:
            left = [x for x in range(ncol) if x < k and not re.search(r'\b(no|nomor)\b\.?', clean(hdr[x]), re.I)]
            for ln, r in rows:
                r = (r + [''] * ncol)[:ncol]
                if is_total_row(r):
                    continue
                stated = num(r[k])
                parts = [num(r[x]) for x in left if num(r[x]) is not None]
                if stated is None or not parts:
                    continue
                checked += 1
                if abs(stated - sum(parts)) > 1e-6:
                    problems.append((path, ln, heading, clean(hdr[k]), stated, sum(parts),
                                     f'baris "{clean(r[1]) or clean(r[0])}"'))
    return problems, checked


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    bad_total, checked_total = 0, 0
    for p in sys.argv[1:]:
        problems, checked = check(p)
        checked_total += checked
        for path, ln, heading, col, stated, comp, where in problems:
            print(f'[TIDAK COCOK] {path}:{ln} | {heading}\n'
                  f'    kolom "{col}", {where}: tertulis {fmt(stated)}, hasil hitung {fmt(comp)} '
                  f'(selisih {fmt(stated - comp)})')
        bad_total += len(problems)
    print(f'\nDiperiksa {checked_total} angka, ketidakcocokan: {bad_total}')
    sys.exit(1 if bad_total else 0)


if __name__ == '__main__':
    main()
