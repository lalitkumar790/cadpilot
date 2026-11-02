$ErrorActionPreference = "Stop"

Write-Host "Removing CADPilot integration..." -ForegroundColor Cyan

$AddonTarget = Join-Path $env:APPDATA "FreeCAD\Mod\AICopilot"
if (Test-Path $AddonTarget) {
    Remove-Item -Path $AddonTarget -Recurse -Force
    Write-Host "Removed $AddonTarget"
} else {
    Write-Host "FreeCAD add-on folder not found; skipping."
}

$ConfigPath = Join-Path $env:APPDATA "Claude\claude_desktop_config.json"
if (Test-Path $ConfigPath) {
    $Config = Get-Content -Raw -Path $ConfigPath | ConvertFrom-Json
    if ($null -ne $Config.mcpServers) {
        $Config.mcpServers.PSObject.Properties.Remove("freecad")
        $Config | ConvertTo-Json -Depth 100 | Set-Content -Path $ConfigPath -Encoding UTF8
        Write-Host "Removed 'freecad' entry from $ConfigPath"
    }
} else {
    Write-Host "Claude config not found; skipping."
}

Write-Host "Uninstall complete. Your CAD documents and project folder were not deleted." -ForegroundColor Green
