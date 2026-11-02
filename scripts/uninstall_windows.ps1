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
            Where-Object { $_.Name -match '^v\d+-\d+$' } |
            Sort-Object -Property @{
                Expression = { [version](($_.Name -replace '^v', '') -replace '-', '.') }
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
$AddonQuarantinePath = $null
$RemoveConfigEntry = $false
$AddonMoved = $false

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

# Quarantine the add-on with a same-volume rename first. Unlike recursive
# deletion, this is reversible and avoids a half-deleted add-on on failure.
if (Test-Path -LiteralPath $AddonTarget -PathType Container) {
    $Stamp = Get-Date -Format "yyyyMMdd-HHmmss-fff"
    $AddonQuarantinePath = Join-Path $ModRoot "AICopilot.uninstall-backup-$Stamp"
    Move-Item -LiteralPath $AddonTarget -Destination $AddonQuarantinePath
    $AddonMoved = $true
    Write-Host "Temporarily moved add-on to $AddonQuarantinePath"
}

try {
    if ($RemoveConfigEntry) {
        $Stamp = Get-Date -Format "yyyyMMdd-HHmmss-fff"
        $ConfigBackupPath = Join-Path (Split-Path $ConfigPath) "claude_desktop_config.backup-$Stamp.json"
        $ConfigTempPath = "$ConfigPath.$Stamp.tmp"
        Copy-Item -LiteralPath $ConfigPath -Destination $ConfigBackupPath

        $Config.mcpServers.PSObject.Properties.Remove("freecad")
        $Json = $Config | ConvertTo-Json -Depth 100
        $Utf8NoBom = New-Object -TypeName System.Text.UTF8Encoding -ArgumentList (,$false)
        [System.IO.File]::WriteAllText($ConfigTempPath, $Json, $Utf8NoBom)
        Move-Item -LiteralPath $ConfigTempPath -Destination $ConfigPath -Force
        Write-Host "Removed 'freecad' entry. Previous config backed up to $ConfigBackupPath"
    } else {
        Write-Host "No 'freecad' entry found in Claude config; skipping."
    }
} catch {
    if ($ConfigTempPath -and (Test-Path -LiteralPath $ConfigTempPath)) {
        Remove-Item -LiteralPath $ConfigTempPath -Force
    }
    if ($AddonMoved -and (Test-Path -LiteralPath $AddonQuarantinePath)) {
        Move-Item -LiteralPath $AddonQuarantinePath -Destination $AddonTarget
        Write-Warning "Restored the FreeCAD add-on because Claude config update failed."
    }
    throw "Uninstall was rolled back. $($_.Exception.Message)"
}

# Configuration is now safely updated. Delete the quarantined add-on only
# after the config write succeeds. If deletion is blocked, retain the backup.
if ($AddonMoved) {
    try {
        Remove-Item -LiteralPath $AddonQuarantinePath -Recurse -Force
        Write-Host "Removed $AddonTarget"
    } catch {
        Write-Warning "Claude config was updated, but the add-on backup could not be deleted. Remove it manually when FreeCAD is closed: $AddonQuarantinePath"
    }
} else {
    Write-Host "FreeCAD add-on not found at $AddonTarget; skipping."
}

Write-Host "Uninstall complete. Your CAD documents, project folder, Python environment, and other add-on backups were not deleted." -ForegroundColor Green
