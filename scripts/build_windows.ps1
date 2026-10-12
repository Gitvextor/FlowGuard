$ErrorActionPreference = "Stop"
python -m PyInstaller --noconfirm packaging/FlowGuard.spec
Write-Host "Windows onedir build created at dist/FlowGuard"
