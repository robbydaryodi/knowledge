# Master Knowledge Base: BCPS 2026
**Program Penyiapan Bakal Calon Pengawas Sekolah (BCPS) Tahun 2026**
*Balai Guru dan Tenaga Kependidikan (BGTK) Provinsi Sumatera Barat*

Repositori pengetahuan ini dibangun dengan arsitektur **Master Knowledge Builder (3 Lapis & 4 Tiers Provenance)** untuk mengelola informasi dari dokumen resmi dan obrolan grup WhatsApp secara terverifikasi, terstruktur, dan anti-halusinasi.

---

## 📁 Struktur Direktori

```text
BCPS/
├── raw/
│   ├── chats/           ← [INPUT] Tempat menaruh file ekspor chat WhatsApp (.txt)
│   └── regulasi/        ← [INPUT] Tempat menaruh surat edaran, juknis, permendikbud (.pdf/.docx)
├── config/
│   ├── people.csv       ← Roster pengirim chat (Nama di WA -> Peran -> Kategori: pusat/upt/dinas/peserta)
│   └── program.md       ← Metadata program, definisi peran, dan alur kerja BCPS 2026
├── ledger/
│   ├── claims.jsonl     ← Sumber kebenaran klaim atomik (T1 s.d. T4 + riwayat status)
│   └── sources.jsonl    ← Audit trail file yang sudah diproses (SHA-256 hash)
├── work/                ← File parsing sementara dari skrip
├── output/
│   ├── L1_peta.md              ← Lapis 1: Peta eksekutif ringkas (1 halaman, T1/T2)
│   ├── L2_verifikator.md       ← Lapis 2: Panduan teknis tim verifikasi berkas
│   ├── L2_pendamping-dinas.md  ← Lapis 2: Panduan pendampingan 19 Kab/Kota
│   ├── L2_pimpinan.md          ← Lapis 2: Panduan pimpinan & indikator risiko
│   ├── L3_rujukan.md           ← Lapis 3: Rujukan lengkap, rekapitulasi, decision log
│   ├── review_queue.md         ← Antrean konflik, T2 menunggu surat, & hal butuh keputusan manusia
│   └── CHANGELOG.md            ← Log riwayat pembaruan knowledge base
└── scripts/
    ├── check_ledger.py         ← Validator keabsahan klaim & provenance
    ├── check_table_sums.py     ← Penguji konsistensi penjumlahan tabel angka
    └── parse_wa_export.py      ← Parser otomatis ekspor chat WhatsApp
```

---

## 🏷️ Derajat Kekuatan Bukti (Source Tiers)

1. 🟢 **T1 (Dasar Hukum)**: Dokumen bernomor resmi (UU, Permen, Kepmen, Surat Edaran Direktur/Dirjen, Juknis).
2. 🟡 **T2 (Penegasan PIC Pusat)**: Arahan lisan/tertulis dari pejabat/PIC Direktorat di grup WhatsApp resmi (berlaku max 14 hari sampai ada surat resmi).
3. 🟠 **T3 (Pihak Lain)**: Praktik atau informasi dari Dinas Pendidikan, BKPSDM, UPT lain, atau peserta (bukan aturan pusat).
4. 🔵 **T4 (Inferensi Penyusun)**: Kesimpulan atau konsekuensi logis turunan dari T1/T2 (wajib memiliki basis ID klaim yang sah).
5. 🔴 **BELUM FINAL**: Informasi yang masih dalam perumusan/draf (tidak boleh dijadikan dasar tindakan hukum).

---

## 🚀 Alur Kerja Saat Anda Mengisi Bahan:

1. **Masukkan File Baru**:
   - Taruh ekspor chat WhatsApp (`.txt`) ke dalam `raw/chats/`
   - Taruh dokumen resmi (`.pdf` / `.docx`) ke dalam `raw/regulasi/`
2. **Cek Roster**:
   - Pastikan nama pengirim chat di `config/people.csv` sudah ada dan diberi kategori yang benar (`pusat`, `upt`, `dinas`, `peserta`).
3. **Minta Antigravity / Agent Memproses**:
   - Cukup ketik perintah: *"Tolong proses dan perbarui master knowledge dari bahan baru"* atau *"Update master knowledge BCPS"*.
   - Sistem akan otomatis menghitung sha256, mengekstrak klaim, memvalidasi integritas data, dan merender ulang dokumen `output/`.
