param(
    [switch]$InstallBuildDependencies
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $projectRoot "backend"
$python = Join-Path $backendRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $python)) {
    throw "Backend-venv fehlt. Führe zuerst das Setup aus: python -m venv backend/.venv"
}

if ($InstallBuildDependencies) {
    & $python -m pip install -r (Join-Path $backendRoot "requirements-build.txt")
}

Push-Location $backendRoot
try {
    & $python -m PyInstaller `
        --noconfirm `
        --clean `
        --onefile `
        --name documind-backend `
        --collect-all chromadb `
        main.py

    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller-Build fehlgeschlagen."
    }

    $tauriResources = Join-Path $projectRoot "frontend\src-tauri\resources"
    New-Item -ItemType Directory -Force -Path $tauriResources | Out-Null
    Copy-Item `
        -LiteralPath (Join-Path $backendRoot "dist\documind-backend.exe") `
        -Destination (Join-Path $tauriResources "documind-backend.exe") `
        -Force
}
finally {
    Pop-Location
}

Write-Host "Backend erstellt und für Tauri bereitgestellt: frontend/src-tauri/resources/documind-backend.exe"
