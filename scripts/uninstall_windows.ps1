param(
    [string]$FreeCADModDirectory
)

$ErrorActionPreference = "Stop"
Write-Host "Removing CADPilot integration..." -ForegroundColor Cyan

# Resolve the same default profile strategy as setup. A custom path is
# intentionally exact: uninstall only the profile the caller selected.
if (-not [string]::IsNullOrWhiteSpace($FreeCADModDirectory)) {
    if (-not (Test-Path -LiteralPath $FreeCADModDirectory -PathType Container)) {
        throw "FreeCAD Mod directory does not exist: $FreeCADModDirectory"
    }
    $ModRoot = (Resolve-Path -LiteralPath $FreeCADModDirectory).Path
} else {
    $FreeCADRoot = Join-Path $env:APPDATA "FreeCAD"
    $VersionedRoots = @()
    if (Test-Path -LiteralPath $FreeCADRoot -PathType Container) {
        $VersionedRoots = @(Get-ChildItem -LiteralPath $FreeCADRoot -Directory -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -match '^v(\d+)-(\d+)$' } |
            Sort-Object @{
                Expression = { [int]([regex]::Match($_.Name, '^v(\d+)-(\d+)$').Groups[1].Value) }
                Descending = $true
            }, @{
                Expression = { [int]([regex]::Match($_.Name, '^v(\d+)-(\d+)$').Groups[2].Value) }
                Descending = $true
            })
    }

    if ($VersionedRoots.Count -gt 0) {
        $ModRoot = Join-Path $VersionedRoots[0].FullName "Mod"
    } else {
        $ModRoot = Join-Path $FreeCADRoot "Mod"
    }
}

$AddonTarget = Join-Path $ModRoot "AICopilot"
$ConfigPath = Join-Path $env:APPDATA "Claude\claude_desktop_config.json"
$Config = $null
$ConfigTempPath = $null
$ConfigBackupPath = $null
$RemoveConfigEntry = $false

# Validate the config before changing either installation. Invalid JSON is
# never overwritten, and the add-on remains installed if config is malformed.
if (Test-Path -LiteralPath $ConfigPath -PathType Leaf) {
    try {
        $Config = Get-Content -Raw -LiteralPath $ConfigPath | ConvertFrom-Json
    } catch {
        throw "Claude config is not valid JSON. Nothing was uninstalled: $ConfigPath"
    }

    if ($null -ne $Config -and $null -ne $Config.PSObject.Properties["mcpServers"]) {
        $Servers = $Config.mcpServers
        if ($null -ne $Servers -and $null -ne $Servers.PSObject.Properties["freecad"]) {
            $RemoveConfigEntry = $true
        }
    }
}

if ($RemoveConfigEntry) {
    $Stamp = Get-Date -Format "yyyyMMdd-HHmmss-fff"
    $ConfigBackupPath = Join-Path (Split-Path $ConfigPath) "claude_desktop_config.backup-$Stamp.json"
    $ConfigTempPath = "$ConfigPath.$Stamp.tmp"
    Copy-Item -LiteralPath $ConfigPath -Destination $ConfigBackupPath
    try {
        $Config.mcpServers.PSObject.Properties.Remove("freecad")
        $Json = $Config | ConvertTo-Json -Depth 100
        [System.IO.File]::WriteAllText($ConfigTempPath, $Json, (New-Object System.Text.UTF8Encoding($false)))
        Move-Item -LiteralPath $ConfigTempPath -Destination $ConfigPath -Force
        Write-Host "Removed 'freecad' entry. Previous config backed up to $ConfigBackupPath"
    } catch {
        if (Test-Path -LiteralPath $ConfigTempPath) {
            Remove-Item -LiteralPath $ConfigTempPath -Force
        }
        throw "Could not safely update Claude config. The add-on was left installed. Backup: $ConfigBackupPath. Error: $_"
    }
} else {
    Write-Host "No 'freecad' entry found in Claude config; skipping."
}

if (Test-Path -LiteralPath $AddonTarget -PathType Container) {
    try {
        Remove-Item -LiteralPath $AddonTarget -Recurse -Force
        Write-Host "Removed $AddonTarget"
    } catch {
        # Restore the previous config if the add-on could not be removed.
        if ($RemoveConfigEntry -and $ConfigBackupPath -and (Test-Path -LiteralPath $ConfigBackupPath)) {
            Copy-Item -LiteralPath $ConfigBackupPath -Destination $ConfigPath -Force
            Write-Warning "Restored Claude config because add-on removal failed."
        }
        throw
    }
} else {
    Write-Host "FreeCAD add-on not found at $AddonTarget; skipping."
}

Write-Host "Uninstall complete. Your CAD documents, project folder, Python environment, and add-on backups were not deleted." -ForegroundColor Green
