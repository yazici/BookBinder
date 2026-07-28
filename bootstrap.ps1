#Requires -Version 5.1
<#
.SYNOPSIS
    BookBinder Bootstrap Script for Windows

.DESCRIPTION
    Installs Python 3, pip, all Python dependencies, Playwright Chromium,
    and optional tools (Java for PlantUML diagram rendering).

.PARAMETER Minimal
    Skip optional tools (Java/PlantUML).

.PARAMETER Upgrade
    Force-upgrade all Python dependencies.

.EXAMPLE
    .\bootstrap.ps1
    .\bootstrap.ps1 -Minimal
    .\bootstrap.ps1 -Upgrade
#>

[CmdletBinding()]
param(
    [switch]$Minimal,
    [switch]$Upgrade
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# --- Configuration ---
$PythonMinVersion = [version]"3.10"
$RequiredPipPackages = @("markdown", "jinja2", "playwright", "pyyaml", "pygments")
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# --- Helpers ---
function Write-Info    { param([string]$Msg) Write-Host "[BookBinder] $Msg" -ForegroundColor Cyan }
function Write-Success { param([string]$Msg) Write-Host "[BookBinder] $Msg" -ForegroundColor Green }
function Write-Warn    { param([string]$Msg) Write-Host "[BookBinder] $Msg" -ForegroundColor Yellow }
function Write-Err     { param([string]$Msg) Write-Host "[BookBinder] $Msg" -ForegroundColor Red }

function Test-Command {
    param([string]$Name)
    $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

# =============================================================================
# Python detection and installation
# =============================================================================
function Find-Python {
    <#
    .DESCRIPTION
        Finds a suitable Python >= 3.10 on the system.
        Returns the command name or $null.
    #>
    foreach ($cmd in @("python", "python3", "py")) {
        if (Test-Command $cmd) {
            try {
                $verOutput = & $cmd --version 2>&1
                if ($verOutput -match "Python (\d+\.\d+(\.\d+)?)") {
                    $ver = [version]$Matches[1]
                    if ($ver -ge $PythonMinVersion) {
                        return $cmd
                    }
                }
            } catch {
                continue
            }
        }
    }

    # Try the py launcher with version flag
    if (Test-Command "py") {
        try {
            $verOutput = & py -3 --version 2>&1
            if ($verOutput -match "Python (\d+\.\d+(\.\d+)?)") {
                $ver = [version]$Matches[1]
                if ($ver -ge $PythonMinVersion) {
                    return "py -3"
                }
            }
        } catch {}
    }

    return $null
}

function Install-Python {
    Write-Info "Python >= $PythonMinVersion not found. Attempting installation..."

    # Try winget first
    if (Test-Command "winget") {
        Write-Info "Installing Python via winget..."
        & winget install --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
        if ($LASTEXITCODE -eq 0) {
            # Refresh PATH
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
            return
        }
    }

    # Try choco
    if (Test-Command "choco") {
        Write-Info "Installing Python via Chocolatey..."
        & choco install python3 -y
        if ($LASTEXITCODE -eq 0) {
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
            return
        }
    }

    # Try scoop
    if (Test-Command "scoop") {
        Write-Info "Installing Python via Scoop..."
        & scoop install python
        if ($LASTEXITCODE -eq 0) {
            return
        }
    }

    Write-Err "Could not install Python automatically."
    Write-Err "Please install Python 3.10+ from https://www.python.org/downloads/"
    Write-Err "Make sure to check 'Add Python to PATH' during installation."
    exit 1
}

function Ensure-Python {
    $script:PythonCmd = Find-Python
    if ($script:PythonCmd) {
        $verOutput = if ($script:PythonCmd -eq "py -3") {
            & py -3 --version 2>&1
        } else {
            & $script:PythonCmd --version 2>&1
        }
        Write-Success "Python found: $verOutput"
    } else {
        Install-Python
        $script:PythonCmd = Find-Python
        if (-not $script:PythonCmd) {
            Write-Err "Failed to install Python >= $PythonMinVersion"
            exit 1
        }
        $verOutput = if ($script:PythonCmd -eq "py -3") {
            & py -3 --version 2>&1
        } else {
            & $script:PythonCmd --version 2>&1
        }
        Write-Success "Python installed: $verOutput"
    }
}

# =============================================================================
# Helper to invoke python (handles "py -3" case)
# =============================================================================
function Invoke-Python {
    param([string[]]$Arguments)
    if ($script:PythonCmd -eq "py -3") {
        & py -3 @Arguments
    } else {
        & $script:PythonCmd @Arguments
    }
}

# =============================================================================
# pip installation
# =============================================================================
function Ensure-Pip {
    $null = Invoke-Python @("-m", "pip", "--version") 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "pip is available."
        return
    }

    Write-Info "Installing pip..."
    Invoke-Python @("-m", "ensurepip", "--upgrade")
    if ($LASTEXITCODE -ne 0) {
        # Fallback: download get-pip.py
        $getPipPath = Join-Path $env:TEMP "get-pip.py"
        Write-Info "Downloading get-pip.py..."
        Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile $getPipPath -UseBasicParsing
        Invoke-Python @($getPipPath)
        Remove-Item $getPipPath -ErrorAction SilentlyContinue
    }

    $null = Invoke-Python @("-m", "pip", "--version") 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "pip installed successfully."
    } else {
        Write-Err "Failed to install pip."
        exit 1
    }
}

# =============================================================================
# Python dependencies
# =============================================================================
function Install-PythonDeps {
    Write-Info "Installing Python dependencies: $($RequiredPipPackages -join ', ')"

    $pipArgs = @("-m", "pip", "install")
    if ($Upgrade) {
        $pipArgs += "--upgrade"
    }
    $pipArgs += $RequiredPipPackages

    Invoke-Python $pipArgs
    if ($LASTEXITCODE -ne 0) {
        Write-Err "Failed to install Python dependencies."
        exit 1
    }
    Write-Success "Python dependencies installed."
}

# =============================================================================
# Playwright Chromium
# =============================================================================
function Install-PlaywrightChromium {
    Write-Info "Installing Playwright Chromium browser..."
    Invoke-Python @("-m", "playwright", "install", "chromium")
    if ($LASTEXITCODE -ne 0) {
        Write-Err "Failed to install Playwright Chromium."
        exit 1
    }
    Write-Success "Playwright Chromium installed."
}

# =============================================================================
# Optional: Java (for PlantUML diagram rendering)
# =============================================================================
function Ensure-Java {
    if (Test-Command "java") {
        $javaVer = & java -version 2>&1 | Select-Object -First 1
        Write-Success "Java found: $javaVer"
        return
    }

    Write-Info "Installing Java (for PlantUML diagram support)..."

    if (Test-Command "winget") {
        & winget install --id Microsoft.OpenJDK.17 --accept-package-agreements --accept-source-agreements
        if ($LASTEXITCODE -eq 0) {
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
            Write-Success "Java installed via winget."
            return
        }
    }

    if (Test-Command "choco") {
        & choco install openjdk17 -y
        if ($LASTEXITCODE -eq 0) {
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
            Write-Success "Java installed via Chocolatey."
            return
        }
    }

    if (Test-Command "scoop") {
        & scoop install openjdk17
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Java installed via Scoop."
            return
        }
    }

    Write-Warn "Java installation failed. PlantUML diagrams will not render."
    Write-Warn "Install manually from https://adoptium.net/"
}

# =============================================================================
# Verification
# =============================================================================
function Test-Installation {
    Write-Info "Verifying installation..."
    $allOk = $true

    # Check Python
    $pythonCheck = Find-Python
    if ($pythonCheck) {
        Write-Success "  ✓ Python"
    } else {
        Write-Err "  ✗ Python >= $PythonMinVersion"
        $allOk = $false
    }

    # Check pip packages
    $importMap = @{
        "markdown"   = "markdown"
        "jinja2"     = "jinja2"
        "playwright" = "playwright"
        "pyyaml"     = "yaml"
        "pygments"   = "pygments"
    }
    foreach ($pkg in $RequiredPipPackages) {
        $mod = $importMap[$pkg]
        $null = Invoke-Python @("-c", "import $mod") 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "  ✓ $pkg"
        } else {
            Write-Err "  ✗ $pkg"
            $allOk = $false
        }
    }

    # Check Playwright Chromium
    $playwrightCheck = @"
from playwright.sync_api import sync_playwright
from pathlib import Path
with sync_playwright() as pw:
    p = Path(pw.chromium.executable_path)
    assert p.is_file()
"@
    $null = Invoke-Python @("-c", $playwrightCheck) 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "  ✓ Playwright Chromium"
    } else {
        Write-Err "  ✗ Playwright Chromium"
        $allOk = $false
    }

    # Check Java (optional)
    if (-not $Minimal) {
        if (Test-Command "java") {
            Write-Success "  ✓ Java (PlantUML support)"
        } else {
            Write-Warn "  ○ Java not available (PlantUML diagrams won't render)"
        }
    }

    Write-Host ""
    if ($allOk) {
        Write-Success "═══════════════════════════════════════════════════"
        Write-Success " BookBinder is ready!"
        Write-Success " Run: python $ScriptDir\make_a_book.py BOOK.md"
        Write-Success "═══════════════════════════════════════════════════"
    } else {
        Write-Err "Some components failed to install. See errors above."
        exit 1
    }
}

# =============================================================================
# Main
# =============================================================================
function Main {
    Write-Host ""
    Write-Info "═══════════════════════════════════════════════════"
    Write-Info " BookBinder Bootstrap (Windows)"
    Write-Info "═══════════════════════════════════════════════════"
    Write-Host ""

    Ensure-Python
    Ensure-Pip
    Install-PythonDeps
    Install-PlaywrightChromium

    if (-not $Minimal) {
        Ensure-Java
    }

    Write-Host ""
    Test-Installation
}

Main