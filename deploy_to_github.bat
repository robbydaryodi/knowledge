@echo off
chcp 65001 >nul
echo ========================================================
echo   Master Knowledge Base BCPS 2026 - GitHub Publisher
echo   Akun GitHub : robbydaryodi
echo   BGTK Provinsi Sumatera Barat - Kemendikdasmen
echo ========================================================
echo.

set /p REPO_NAME="Masukkan nama repositori GitHub [default: bcps-knowledge-2026]: "
if "%REPO_NAME%"=="" set REPO_NAME=bcps-knowledge-2026

echo.
echo [*] Memperbarui basis data portal site/data.json...
python scripts\update_site_data.py

echo.
echo [1/4] Menginisialisasi Git Repositori Tunggal...
if not exist .git (
    git init
    git branch -M main
)

echo.
echo [2/4] Menambahkan seluruh berkas master knowledge...
git add .
git commit -m "feat: publish master knowledge base bcps 2026 (ledger, docs, portal)"

echo.
echo [3/4] Menghubungkan remote GitHub https://github.com/robbydaryodi/%REPO_NAME%.git ...
git remote remove origin 2>nul
git remote add origin https://github.com/robbydaryodi/%REPO_NAME%.git

echo.
echo [4/4] Melakukan Push ke cabang main...
git push -u origin main

echo.
echo ========================================================
echo   PUSH SELESAI!
echo ========================================================
echo.
echo LANGKAH PENGAKTIFAN GITHUB PAGES (Hanya 1 Kali):
echo 1. Buka: https://github.com/robbydaryodi/%REPO_NAME%/settings/pages
echo 2. Pada opsi 'Build and deployment' -> 'Source':
echo    Pilih: [GitHub Actions]
echo 3. Selesai! Workflow deploy-pages.yml akan otomatis mempublikasikan portal.
echo.
echo Portal Publik Anda akan aktif di:
echo 👉 https://robbydaryodi.github.io/%REPO_NAME%/
echo ========================================================
echo.
pause
