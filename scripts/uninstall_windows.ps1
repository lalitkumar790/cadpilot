$ErrorActionPreference = "Stop"
Write-Host "Removing CADPilot integration..." -ForegroundColor Cyan

$FreeCADRoot = Join-Path $env:APPDATA "FreeCAD"
$AddonTargets = @()
$DefaultTarget = Join-Path $FreeCADRoot "Mod\AICopilot"
if (Test-Path $DefaultTarget) { $AddonTargets += $DefaultTarget }

if (Test-Path $FreeCADRoot) {
    Get-ChildItem -Path $FreeCADRoot -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match '^v\d+-\d+$' } |
        ForEach-Object {
            $candidate = Join-Path $_.FullName "Mod\AICopilot"
            if (Test-Path $candidate) { $AddonTargets += $candidate }
        }
}

$AddonTargets = @($AddonTargets | Select-Object -Unique)
if ($AddonTargets.Count -eq 0) {
    Write-Host "FreeCAD add-on folder not found; skipping."
} else {
    foreach ($target in $AddonTargets) {
        Remove-Item -LiteralPath $target -Recurse -Force
        Write-Host "Removed $target"
    }
}

$ConfigPath = Join-Path $env:APPDATA "Claude\claude_desktop_config.json"
if (Test-Path $ConfigPath) {
    try {
        $Config = Get-Content -Raw -Path $ConfigPath | ConvertFrom-Json
    } catch {
        throw "Claude config is not valid JSON. It was left untouched: $ConfigPath"
    }

    if ($null -ne $Config.mcpServers -and $null -ne $Config.mcpServers.PSObject.Properties["freecad"]) {
        $Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
        $BackupPath = Join-Path (Split-Path $ConfigPath) "claude_desktop_config.backup-$Stamp.json"
        Copy-Item -LiteralPath $ConfigPath -Destination $BackupPath
        $Config.mcpServers.PSObject.Properties.Remove("freecad")
        $TempPath = "$ConfigPath.tmp"
        $Json = $Config | ConvertTo-Json -Depth 100
        [System.IO.File]::WriteAllText($TempPath, $Json, (New-Object System.Text.UTF8Encoding($false)))
        Move-Item -LiteralPath $TempPath -Destination $ConfigPath -Force
        Write-Host "Removed 'freecad' entry. Previous config backed up to $BackupPath"
    } else {
        Write-Host "No 'freecad' entry found in Claude config; skipping."
    }
} else {
    Write-Host "Claude config not found; skipping."
}

Write-Host "Uninstall complete. Your CAD documents and project folder were not deleted." -ForegroundColor Green
