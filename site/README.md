# Master Knowledge Base: Uji Kompetensi Pengawas Sekolah & BCPS 2026
**Balai Guru dan Tenaga Kependidikan (BGTK) Provinsi Sumatera Barat**  
*Kementerian Pendidikan Dasar dan Menengah*

Repositori ini memuat **Portal Interaktif Web** dan **Knowledge Base 3 Lapis & 4 Tiers Provenance** untuk Uji Kompetensi Jabatan Fungsional Pengawas Sekolah (UKPJ & UKKJ) Tahun 2026.

---

## 🌐 Akses Web Portal
Aplikasi web responsif telah siap dihosting langsung via **GitHub Pages**.  
File utama: [`index.html`](index.html) dan data rekapitulasi: [`data.json`](data.json).

### Fitur Web Knowledge:
1. **Navigasi 3 Lapis Dokumen**:
   - **Lapis 1 (Peta Eksekutif)**: Ringkasan kalender kritis, tenggat urut waktu, dan aksi mendesak.
   - **Lapis 2 (Panduan Peran)**: Khusus Tim Verifikator UPT BGTK Sumbar, Pendamping 19 Dinas Kab/Kota, dan Laporan Pimpinan.
   - **Lapis 3 (Rujukan Lengkap)**: Ledger lengkap 39 klaim atomik terverifikasi beserta decision log.
2. **Interactive Claims Ledger Explorer**:
   - Filter tabel instan berdasarkan **Tier (T1 Dasar Hukum, T2 Penegasan Pusat, T4 Inferensi)**.
   - Filter berdasarkan Lapis dokumen (1, 2, 3).
   - Kotak pencarian cepat (kata kunci, topik, atau ID klaim).
3. **Audit Trail & Review Queue**:
   - Pemantauan status pendaftar ganda dan masa berlaku regulasi.

---

## 🚀 Cara Mengaktifkan GitHub Pages:
1. Buat repositori baru di akun GitHub Anda (misal: `bcps-knowledge-2026`).
2. Masuk ke folder ini (`site/`) dan jalankan:
   ```bash
   git init
   git add .
   git commit -m "feat: inisialisasi portal master knowledge bcps 2026"
   git branch -M main
   git remote add origin https://github.com/robbydaryodi/<nama-repo>.git
   git push -u origin main
   ```
3. Buka tab **Settings** di GitHub > **Pages** > pilih branch `main` folder `/ (root)` > Simpan.
4. Web akan aktif di: `https://robbydaryodi.github.io/<nama-repo>/`.

---
*Dikelola oleh Robby Daryodi, S.Kom. — BGTK Provinsi Sumatera Barat.*
