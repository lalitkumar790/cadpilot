param(
    [switch]$SkipFreeCADAddon,
    [switch]$SkipClaudeConfig,
    [string]$FreeCADModDirectory
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

Write-Host ""
Write-Host "CADPilot - Student Setup" -ForegroundColor Cyan
Write-Host "Project: $RepoRoot"
Write-Host ""

# Prefer the Python Launcher and select the newest supported interpreter.
$PythonCommand = $null
$PythonPrefixArgs = @()
if (Get-Command py -ErrorAction SilentlyContinue) {
    foreach ($Candidate in @("-3.13", "-3.12", "-3.11")) {
        try {
            & py $Candidate --version | Out-Null
            if ($LASTEXITCODE -eq 0) {
                $PythonCommand = "py"
                $PythonPrefixArgs = @($Candidate)
                break
            }
        } catch {}
    }
}

if (-not $PythonCommand -and (Get-Command python -ErrorAction SilentlyContinue)) {
    $PythonCommand = "python"
}

if (-not $PythonCommand) {
    throw "Python 3.11+ was not found. Install Python 3.11+ from https://www.python.org/downloads/windows/ and rerun this script."
}

$VersionText = (& $PythonCommand @PythonPrefixArgs --version 2>&1 | Out-String).Trim()
if ($VersionText -notmatch "Python (\d+)\.(\d+)") {
    throw "Could not determine Python version from: $VersionText"
}
$Major = [int]$Matches[1]
$Minor = [int]$Matches[2]
if (($Major -lt 3) -or (($Major -eq 3) -and ($Minor -lt 11))) {
    throw "Found $VersionText. The MCP Python SDK v2 requires Python 3.11 or newer."
}
Write-Host "Using $VersionText"

$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Host "Creating virtual environment..."
    & $PythonCommand @PythonPrefixArgs -m venv (Join-Path $RepoRoot ".venv")
    if ($LASTEXITCODE -ne 0) { throw "Could not create Python virtual environment." }
}

Write-Host "Installing project and dependencies..."
& $VenvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed." }
& $VenvPython -m pip install -e $RepoRoot
if ($LASTEXITCODE -ne 0) { throw "Project installation failed." }

if (-not $SkipFreeCADAddon) {
    if ([string]::IsNullOrWhiteSpace($FreeCADModDirectory)) {
        $FreeCADRoot = Join-Path $env:APPDATA "FreeCAD"
        # FreeCAD 1.0 commonly uses FreeCAD\\Mod; 1.1+ may use
        # a version-specific user-data directory such as FreeCAD\\v1-1\\Mod.
        $VersionedRoots = @(Get-ChildItem -Path $FreeCADRoot -Directory -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -match '^v\d+-\d+
        if ($VersionedRoots.Count -gt 0) {
            $ModRoot = Join-Path $VersionedRoots[0].FullName "Mod"
        } else {
            $ModRoot = Join-Path $FreeCADRoot "Mod"
        }
    } else {
        $ModRoot = (Resolve-Path -LiteralPath $FreeCADModDirectory).Path
    }
    $AddonSource = Join-Path $RepoRoot "AICopilot"
    $RequiredAddonFiles = @(
        "InitGui.py",
        "socket_server.py",
        "security_policy.py",
        "request_validation.py",
        "export_validation.py"
    )
    foreach ($RequiredFile in $RequiredAddonFiles) {
        $SourceFile = Join-Path $AddonSource $RequiredFile
        if (-not (Test-Path -LiteralPath $SourceFile -PathType Leaf)) {
            throw "Required FreeCAD add-on file is missing: $SourceFile. Re-download or re-extract the complete CADPilot repository."
        }
    }

    $AddonTarget = Join-Path $ModRoot "AICopilot"
    New-Item -ItemType Directory -Force -Path $ModRoot | Out-Null

    $Backup = $null
    if (Test-Path -LiteralPath $AddonTarget) {
        $Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
        $Backup = Join-Path $ModRoot "AICopilot.backup-$Stamp"
        Write-Host "Backing up existing add-on to $Backup"
        Move-Item -LiteralPath $AddonTarget -Destination $Backup
    }

    try {
        Copy-Item -LiteralPath $AddonSource -Destination $AddonTarget -Recurse -Force
        foreach ($RequiredFile in $RequiredAddonFiles) {
            $InstalledFile = Join-Path $AddonTarget $RequiredFile
            if (-not (Test-Path -LiteralPath $InstalledFile -PathType Leaf)) {
                throw "Add-on installation verification failed; missing: $InstalledFile"
            }
        }
    } catch {
        # Never leave a previously working add-on stranded in its backup
        # location after an interrupted or incomplete update.
        if (Test-Path -LiteralPath $AddonTarget) {
            Remove-Item -LiteralPath $AddonTarget -Recurse -Force
        }
        if ($Backup -and (Test-Path -LiteralPath $Backup)) {
            Move-Item -LiteralPath $Backup -Destination $AddonTarget
            Write-Warning "Restored the previous FreeCAD add-on from $Backup"
        }
        throw
    }
    Write-Host "Verified FreeCAD workbench files: $AddonTarget" -ForegroundColor Green
}

if (-not $SkipClaudeConfig) {
    Write-Host "Configuring Claude Desktop..."
    & $VenvPython (Join-Path $PSScriptRoot "configure_claude.py") --repo-root $RepoRoot
    if ($LASTEXITCODE -ne 0) { throw "Claude Desktop configuration failed." }
}

Write-Host ""
Write-Host "Setup completed." -ForegroundColor Green
if (-not $SkipFreeCADAddon) {
    Write-Host "NEXT: Start/restart FreeCAD and check the Python console for the AI Copilot startup message."
}
if (-not $SkipClaudeConfig) {
    Write-Host "NEXT: Completely quit and restart Claude Desktop."
}
Write-Host "Then ask Claude to call check_freecad_connection."
 } |
            Sort-Object @{
                Expression = { [int]([regex]::Match($_.Name, '^v(\d+)-(\d+)
        if ($VersionedRoots.Count -gt 0) {
            $ModRoot = Join-Path $VersionedRoots[0].FullName "Mod"
        } else {
            $ModRoot = Join-Path $FreeCADRoot "Mod"
        }
    } else {
        $ModRoot = (Resolve-Path -LiteralPath $FreeCADModDirectory).Path
    }
    $AddonSource = Join-Path $RepoRoot "AICopilot"
    $RequiredAddonFiles = @(
        "InitGui.py",
        "socket_server.py",
        "security_policy.py",
        "request_validation.py",
        "export_validation.py"
    )
    foreach ($RequiredFile in $RequiredAddonFiles) {
        $SourceFile = Join-Path $AddonSource $RequiredFile
        if (-not (Test-Path -LiteralPath $SourceFile -PathType Leaf)) {
            throw "Required FreeCAD add-on file is missing: $SourceFile. Re-download or re-extract the complete CADPilot repository."
        }
    }

    $AddonTarget = Join-Path $ModRoot "AICopilot"
    New-Item -ItemType Directory -Force -Path $ModRoot | Out-Null

    $Backup = $null
    if (Test-Path -LiteralPath $AddonTarget) {
        $Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
        $Backup = Join-Path $ModRoot "AICopilot.backup-$Stamp"
        Write-Host "Backing up existing add-on to $Backup"
        Move-Item -LiteralPath $AddonTarget -Destination $Backup
    }

    try {
        Copy-Item -LiteralPath $AddonSource -Destination $AddonTarget -Recurse -Force
        foreach ($RequiredFile in $RequiredAddonFiles) {
            $InstalledFile = Join-Path $AddonTarget $RequiredFile
            if (-not (Test-Path -LiteralPath $InstalledFile -PathType Leaf)) {
                throw "Add-on installation verification failed; missing: $InstalledFile"
            }
        }
    } catch {
        # Never leave a previously working add-on stranded in its backup
        # location after an interrupted or incomplete update.
        if (Test-Path -LiteralPath $AddonTarget) {
            Remove-Item -LiteralPath $AddonTarget -Recurse -Force
        }
        if ($Backup -and (Test-Path -LiteralPath $Backup)) {
            Move-Item -LiteralPath $Backup -Destination $AddonTarget
            Write-Warning "Restored the previous FreeCAD add-on from $Backup"
        }
        throw
    }
    Write-Host "Verified FreeCAD workbench files: $AddonTarget" -ForegroundColor Green
}

if (-not $SkipClaudeConfig) {
    Write-Host "Configuring Claude Desktop..."
    & $VenvPython (Join-Path $PSScriptRoot "configure_claude.py") --repo-root $RepoRoot
    if ($LASTEXITCODE -ne 0) { throw "Claude Desktop configuration failed." }
}

Write-Host ""
Write-Host "Setup completed." -ForegroundColor Green
if (-not $SkipFreeCADAddon) {
    Write-Host "NEXT: Start/restart FreeCAD and check the Python console for the AI Copilot startup message."
}
if (-not $SkipClaudeConfig) {
    Write-Host "NEXT: Completely quit and restart Claude Desktop."
}
Write-Host "Then ask Claude to call check_freecad_connection."
).Groups[1].Value) }
                Descending = $true
            }, @{
                Expression = { [int]([regex]::Match($_.Name, '^v(\d+)-(\d+)
        if ($VersionedRoots.Count -gt 0) {
            $ModRoot = Join-Path $VersionedRoots[0].FullName "Mod"
        } else {
            $ModRoot = Join-Path $FreeCADRoot "Mod"
        }
    } else {
        $ModRoot = (Resolve-Path -LiteralPath $FreeCADModDirectory).Path
    }
    $AddonSource = Join-Path $RepoRoot "AICopilot"
    $RequiredAddonFiles = @(
        "InitGui.py",
        "socket_server.py",
        "security_policy.py",
        "request_validation.py",
        "export_validation.py"
    )
    foreach ($RequiredFile in $RequiredAddonFiles) {
        $SourceFile = Join-Path $AddonSource $RequiredFile
        if (-not (Test-Path -LiteralPath $SourceFile -PathType Leaf)) {
            throw "Required FreeCAD add-on file is missing: $SourceFile. Re-download or re-extract the complete CADPilot repository."
        }
    }

    $AddonTarget = Join-Path $ModRoot "AICopilot"
    New-Item -ItemType Directory -Force -Path $ModRoot | Out-Null

    $Backup = $null
    if (Test-Path -LiteralPath $AddonTarget) {
        $Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
        $Backup = Join-Path $ModRoot "AICopilot.backup-$Stamp"
        Write-Host "Backing up existing add-on to $Backup"
        Move-Item -LiteralPath $AddonTarget -Destination $Backup
    }

    try {
        Copy-Item -LiteralPath $AddonSource -Destination $AddonTarget -Recurse -Force
        foreach ($RequiredFile in $RequiredAddonFiles) {
            $InstalledFile = Join-Path $AddonTarget $RequiredFile
            if (-not (Test-Path -LiteralPath $InstalledFile -PathType Leaf)) {
                throw "Add-on installation verification failed; missing: $InstalledFile"
            }
        }
    } catch {
        # Never leave a previously working add-on stranded in its backup
        # location after an interrupted or incomplete update.
        if (Test-Path -LiteralPath $AddonTarget) {
            Remove-Item -LiteralPath $AddonTarget -Recurse -Force
        }
        if ($Backup -and (Test-Path -LiteralPath $Backup)) {
            Move-Item -LiteralPath $Backup -Destination $AddonTarget
            Write-Warning "Restored the previous FreeCAD add-on from $Backup"
        }
        throw
    }
    Write-Host "Verified FreeCAD workbench files: $AddonTarget" -ForegroundColor Green
}

if (-not $SkipClaudeConfig) {
    Write-Host "Configuring Claude Desktop..."
    & $VenvPython (Join-Path $PSScriptRoot "configure_claude.py") --repo-root $RepoRoot
    if ($LASTEXITCODE -ne 0) { throw "Claude Desktop configuration failed." }
}

Write-Host ""
Write-Host "Setup completed." -ForegroundColor Green
if (-not $SkipFreeCADAddon) {
    Write-Host "NEXT: Start/restart FreeCAD and check the Python console for the AI Copilot startup message."
}
if (-not $SkipClaudeConfig) {
    Write-Host "NEXT: Completely quit and restart Claude Desktop."
}
Write-Host "Then ask Claude to call check_freecad_connection."
).Groups[2].Value) }
                Descending = $true
            })
        if ($VersionedRoots.Count -gt 0) {
            $ModRoot = Join-Path $VersionedRoots[0].FullName "Mod"
        } else {
            $ModRoot = Join-Path $FreeCADRoot "Mod"
        }
    } else {
        $ModRoot = (Resolve-Path -LiteralPath $FreeCADModDirectory).Path
    }
    $AddonSource = Join-Path $RepoRoot "AICopilot"
    $RequiredAddonFiles = @(
        "InitGui.py",
        "socket_server.py",
        "security_policy.py",
        "request_validation.py",
        "export_validation.py"
    )
    foreach ($RequiredFile in $RequiredAddonFiles) {
        $SourceFile = Join-Path $AddonSource $RequiredFile
        if (-not (Test-Path -LiteralPath $SourceFile -PathType Leaf)) {
            throw "Required FreeCAD add-on file is missing: $SourceFile. Re-download or re-extract the complete CADPilot repository."
        }
    }

    $AddonTarget = Join-Path $ModRoot "AICopilot"
    New-Item -ItemType Directory -Force -Path $ModRoot | Out-Null

    $Backup = $null
    if (Test-Path -LiteralPath $AddonTarget) {
        $Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
        $Backup = Join-Path $ModRoot "AICopilot.backup-$Stamp"
        Write-Host "Backing up existing add-on to $Backup"
        Move-Item -LiteralPath $AddonTarget -Destination $Backup
    }

    try {
        Copy-Item -LiteralPath $AddonSource -Destination $AddonTarget -Recurse -Force
        foreach ($RequiredFile in $RequiredAddonFiles) {
            $InstalledFile = Join-Path $AddonTarget $RequiredFile
            if (-not (Test-Path -LiteralPath $InstalledFile -PathType Leaf)) {
                throw "Add-on installation verification failed; missing: $InstalledFile"
            }
        }
    } catch {
        # Never leave a previously working add-on stranded in its backup
        # location after an interrupted or incomplete update.
        if (Test-Path -LiteralPath $AddonTarget) {
            Remove-Item -LiteralPath $AddonTarget -Recurse -Force
        }
        if ($Backup -and (Test-Path -LiteralPath $Backup)) {
            Move-Item -LiteralPath $Backup -Destination $AddonTarget
            Write-Warning "Restored the previous FreeCAD add-on from $Backup"
        }
        throw
    }
    Write-Host "Verified FreeCAD workbench files: $AddonTarget" -ForegroundColor Green
}

if (-not $SkipClaudeConfig) {
    Write-Host "Configuring Claude Desktop..."
    & $VenvPython (Join-Path $PSScriptRoot "configure_claude.py") --repo-root $RepoRoot
    if ($LASTEXITCODE -ne 0) { throw "Claude Desktop configuration failed." }
}

Write-Host ""
Write-Host "Setup completed." -ForegroundColor Green
if (-not $SkipFreeCADAddon) {
    Write-Host "NEXT: Start/restart FreeCAD and check the Python console for the AI Copilot startup message."
}
if (-not $SkipClaudeConfig) {
    Write-Host "NEXT: Completely quit and restart Claude Desktop."
}
Write-Host "Then ask Claude to call check_freecad_connection."
