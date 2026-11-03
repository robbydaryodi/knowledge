Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Master Knowledge Base BCPS 2026 - GitHub Publisher" -ForegroundColor Yellow
Write-Host "  Akun GitHub : robbydaryodi" -ForegroundColor Cyan
Write-Host "  BGTK Provinsi Sumatera Barat - Kemendikdasmen" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

$repoName = Read-Host "Masukkan nama repositori GitHub [default: knowledge]"
if ([string]::IsNullOrWhiteSpace($repoName)) {
    $repoName = "knowledge"
}

Write-Host "`n[*] Memperbarui data portal site/data.json..." -ForegroundColor Green
python scripts/update_site_data.py

Write-Host "`n[1/4] Memeriksa Git..." -ForegroundColor Green
if (-not (Test-Path .git)) {
    git init
    git branch -M main
}

Write-Host "`n[2/4] Menambahkan seluruh berkas..." -ForegroundColor Green
git add .
git commit -m "feat: publish master knowledge base bcps 2026 (ledger, docs, portal)"

Write-Host "`n[3/4] Menghubungkan remote GitHub https://github.com/robbydaryodi/$repoName.git ..." -ForegroundColor Green
git remote remove origin 2>$null
git remote add origin "https://github.com/robbydaryodi/$repoName.git"

Write-Host "`n[4/4] Melakukan Push ke cabang main..." -ForegroundColor Green
git push -u origin main

Write-Host "`n========================================================" -ForegroundColor Cyan
Write-Host "  PROSES PUSH SELESAI!" -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "LANGKAH PENGAKTIFAN GITHUB PAGES (Hanya 1 Kali):"
Write-Host "1. Buka: https://github.com/robbydaryodi/$repoName/settings/pages"
Write-Host "2. Pada opsi 'Build and deployment' -> 'Source':"
Write-Host "   Pilih: [GitHub Actions]"
Write-Host "3. Selesai! Web Anda akan live di:"
Write-Host "   https://robbydaryodi.github.io/$repoName/" -ForegroundColor Green
Write-Host "========================================================`n"
Read-Host "Tekan Enter untuk menutup..."
