# Architecture Diagram Fix Script
# Run this script to automatically fix the architecture diagram issue

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Architecture Diagram Fix Script" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$workspaceDir = "C:\Users\Gebruiker\source\repos\WhereSpace"

# Step 1: Navigate to workspace
Write-Host "[1/7] Navigating to workspace..." -ForegroundColor Yellow
Set-Location $workspaceDir
Write-Host "? Current directory: $(Get-Location)`n" -ForegroundColor Green

# Step 2: Check if Flask is running
Write-Host "[2/7] Checking for running Flask processes..." -ForegroundColor Yellow
$flaskProcess = Get-Process python -ErrorAction SilentlyContinue
if ($flaskProcess) {
    Write-Host "? Flask is running. Please stop it (Ctrl+C) and run this script again." -ForegroundColor Red
    exit 1
} else {
    Write-Host "? No Flask process detected`n" -ForegroundColor Green
}

# Step 3: Clear Python cache
Write-Host "[3/7] Clearing Python cache..." -ForegroundColor Yellow
$cacheCount = 0
Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
    $cacheCount++
}
Get-ChildItem -Path . -Recurse -File -Filter "*.pyc" -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
}
Write-Host "? Cleared $cacheCount cache directories`n" -ForegroundColor Green

# Step 4: Verify mermaid.min.js exists
Write-Host "[4/7] Checking mermaid.min.js file..." -ForegroundColor Yellow
$mermaidPath = "static\mermaid.min.js"
if (Test-Path $mermaidPath) {
    $fileSize = (Get-Item $mermaidPath).Length
    if ($fileSize -eq 3338725) {
        Write-Host "? Mermaid file exists and has correct size ($fileSize bytes)`n" -ForegroundColor Green
    } else {
        Write-Host "? Mermaid file has wrong size: $fileSize (expected: 3338725)" -ForegroundColor Yellow
        Write-Host "  Downloading correct version..." -ForegroundColor Yellow
        curl -L -o $mermaidPath https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js
        Write-Host "? Mermaid file re-downloaded`n" -ForegroundColor Green
    }
} else {
    Write-Host "? Mermaid file not found! Downloading..." -ForegroundColor Red
    New-Item -ItemType Directory -Force -Path static | Out-Null
    curl -L -o $mermaidPath https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js
    Write-Host "? Mermaid file downloaded`n" -ForegroundColor Green
}

# Step 5: Check template for CDN references
Write-Host "[5/7] Checking template for CDN references..." -ForegroundColor Yellow
$cdnRefs = Select-String -Path "templates\architecture.html" -Pattern "cdn.jsdelivr" -ErrorAction SilentlyContinue
if ($cdnRefs) {
    Write-Host "? ERROR: Template still has CDN references!" -ForegroundColor Red
    $cdnRefs | ForEach-Object { Write-Host "  Line $($_.LineNumber): $($_.Line.Trim())" -ForegroundColor Red }
    Write-Host "`n? Template needs manual fix!`n" -ForegroundColor Yellow
} else {
    Write-Host "? Template has no CDN references`n" -ForegroundColor Green
}

# Step 6: Check template for local file reference
Write-Host "[6/7] Checking template for local file reference..." -ForegroundColor Yellow
$localRef = Select-String -Path "templates\architecture.html" -Pattern "url_for\('static', filename='mermaid.min.js'\)" -ErrorAction SilentlyContinue
if ($localRef) {
    Write-Host "? Template correctly references local file`n" -ForegroundColor Green
} else {
    Write-Host "? ERROR: Template doesn't reference local file!" -ForegroundColor Red
    Write-Host "  Expected: url_for('static', filename='mermaid.min.js')`n" -ForegroundColor Red
}

# Step 7: Summary
Write-Host "[7/7] Summary:" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Fix Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "1. Start Flask: python main.py" -ForegroundColor White
Write-Host "2. Test static file: http://127.0.0.1:5000/static/mermaid.min.js" -ForegroundColor White
Write-Host "3. Open Incognito window (Ctrl+Shift+N)" -ForegroundColor White
Write-Host "4. Navigate to: http://127.0.0.1:5000/architecture" -ForegroundColor White
Write-Host "5. Press F12 ? Console tab" -ForegroundColor White
Write-Host "6. Look for: 'Mermaid script loaded from local file'" -ForegroundColor White
Write-Host ""
Write-Host "If diagram still doesn't load:" -ForegroundColor Yellow
Write-Host "- Make sure you're using Incognito window" -ForegroundColor Yellow
Write-Host "- Press Ctrl+Shift+R to hard refresh" -ForegroundColor Yellow
Write-Host "- Check console for exact error messages" -ForegroundColor Yellow
Write-Host ""
