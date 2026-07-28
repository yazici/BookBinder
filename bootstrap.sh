#!/usr/bin/env bash
# =============================================================================
# BookBinder Bootstrap Script
# =============================================================================
# Installs Python 3, pip, all Python dependencies, Playwright Chromium,
# and optional tools (Java for PlantUML diagram rendering).
#
# Usage:
#   ./bootstrap.sh            # Full install
#   ./bootstrap.sh --minimal  # Skip optional tools (Java/PlantUML)
#   ./bootstrap.sh --upgrade  # Force-upgrade all dependencies
#
# Supported platforms: Linux (apt/yum/dnf), macOS (brew), Windows (WSL)
# =============================================================================

set -euo pipefail

# --- Configuration ---
PYTHON_MIN_VERSION="3.10"
REQUIRED_PIP_PACKAGES=(markdown jinja2 playwright pyyaml pygments)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# --- Helpers ---
info()    { echo -e "${BLUE}[BookBinder]${NC} $*"; }
success() { echo -e "${GREEN}[BookBinder]${NC} $*"; }
warn()    { echo -e "${YELLOW}[BookBinder]${NC} $*"; }
error()   { echo -e "${RED}[BookBinder]${NC} $*" >&2; }

die() {
    error "$@"
    exit 1
}

# --- Parse arguments ---
MINIMAL=false
UPGRADE=false
for arg in "$@"; do
    case "$arg" in
        --minimal)  MINIMAL=true ;;
        --upgrade)  UPGRADE=true ;;
        --help|-h)
            echo "Usage: $0 [--minimal] [--upgrade]"
            echo ""
            echo "Options:"
            echo "  --minimal   Skip optional tools (Java, PlantUML)"
            echo "  --upgrade   Force-upgrade all Python dependencies"
            echo "  --help      Show this help message"
            exit 0
            ;;
        *) die "Unknown argument: $arg" ;;
    esac
done

# =============================================================================
# Detect OS and package manager
# =============================================================================
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        if command -v brew &>/dev/null; then
            PKG_MGR="brew"
        else
            die "Homebrew not found. Install it from https://brew.sh"
        fi
    elif [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS="linux"
        if command -v apt-get &>/dev/null; then
            PKG_MGR="apt"
        elif command -v dnf &>/dev/null; then
            PKG_MGR="dnf"
        elif command -v yum &>/dev/null; then
            PKG_MGR="yum"
        elif command -v pacman &>/dev/null; then
            PKG_MGR="pacman"
        elif command -v zypper &>/dev/null; then
            PKG_MGR="zypper"
        else
            die "No supported package manager found (apt, dnf, yum, pacman, zypper)"
        fi
    else
        die "Unsupported operating system: $OSTYPE"
    fi
    info "Detected: OS=$OS, Package Manager=$PKG_MGR"
}

# =============================================================================
# Python installation
# =============================================================================
version_ge() {
    # Returns 0 if $1 >= $2 (semantic version comparison)
    printf '%s\n%s' "$2" "$1" | sort -V -C
}

find_python() {
    # Try python3 first, then python
    for cmd in python3 python; do
        if command -v "$cmd" &>/dev/null; then
            local ver
            ver=$("$cmd" --version 2>&1 | grep -oP '\d+\.\d+(\.\d+)?' | head -1)
            if version_ge "$ver" "$PYTHON_MIN_VERSION"; then
                PYTHON_CMD="$cmd"
                PYTHON_VERSION="$ver"
                return 0
            fi
        fi
    done
    return 1
}

install_python() {
    info "Installing Python >= $PYTHON_MIN_VERSION..."
    case "$PKG_MGR" in
        apt)
            sudo apt-get update -qq
            sudo apt-get install -y python3 python3-pip python3-venv
            ;;
        dnf)
            sudo dnf install -y python3 python3-pip
            ;;
        yum)
            sudo yum install -y python3 python3-pip
            ;;
        pacman)
            sudo pacman -Sy --noconfirm python python-pip
            ;;
        zypper)
            sudo zypper install -y python3 python3-pip
            ;;
        brew)
            brew install python@3.12
            ;;
    esac
}

ensure_python() {
    if find_python; then
        success "Python $PYTHON_VERSION found: $(command -v $PYTHON_CMD)"
    else
        warn "Python >= $PYTHON_MIN_VERSION not found."
        install_python
        if find_python; then
            success "Python $PYTHON_VERSION installed successfully."
        else
            die "Failed to install Python >= $PYTHON_MIN_VERSION"
        fi
    fi
}

# =============================================================================
# pip installation
# =============================================================================
ensure_pip() {
    if "$PYTHON_CMD" -m pip --version &>/dev/null; then
        success "pip is available."
        return
    fi

    info "Installing pip..."
    "$PYTHON_CMD" -m ensurepip --upgrade 2>/dev/null || {
        # ensurepip not available, try get-pip.py
        local get_pip="/tmp/get-pip.py"
        curl -sSL https://bootstrap.pypa.io/get-pip.py -o "$get_pip"
        "$PYTHON_CMD" "$get_pip" --user
        rm -f "$get_pip"
    }

    if "$PYTHON_CMD" -m pip --version &>/dev/null; then
        success "pip installed successfully."
    else
        die "Failed to install pip."
    fi
}

# =============================================================================
# Python dependencies
# =============================================================================
install_python_deps() {
    info "Installing Python dependencies: ${REQUIRED_PIP_PACKAGES[*]}"

    local pip_args=("$PYTHON_CMD" -m pip install)
    if [[ "$UPGRADE" == true ]]; then
        pip_args+=(--upgrade)
    fi

    "${pip_args[@]}" "${REQUIRED_PIP_PACKAGES[@]}"
    success "Python dependencies installed."
}

# =============================================================================
# Playwright Chromium
# =============================================================================
install_playwright_chromium() {
    info "Installing Playwright Chromium browser..."

    # Install system dependencies for Playwright (Linux only)
    if [[ "$OS" == "linux" ]]; then
        "$PYTHON_CMD" -m playwright install-deps chromium 2>/dev/null || true
    fi

    "$PYTHON_CMD" -m playwright install chromium
    success "Playwright Chromium installed."
}

# =============================================================================
# Optional: Java (for PlantUML diagram rendering)
# =============================================================================
ensure_java() {
    if command -v java &>/dev/null; then
        local java_ver
        java_ver=$(java -version 2>&1 | head -1)
        success "Java found: $java_ver"
        return
    fi

    info "Installing Java (for PlantUML diagram support)..."
    case "$PKG_MGR" in
        apt)
            sudo apt-get install -y default-jre-headless
            ;;
        dnf)
            sudo dnf install -y java-17-openjdk-headless
            ;;
        yum)
            sudo yum install -y java-17-openjdk-headless
            ;;
        pacman)
            sudo pacman -Sy --noconfirm jre-openjdk-headless
            ;;
        zypper)
            sudo zypper install -y java-17-openjdk-headless
            ;;
        brew)
            brew install openjdk
            ;;
    esac

    if command -v java &>/dev/null; then
        success "Java installed."
    else
        warn "Java installation failed. PlantUML diagrams will not render."
    fi
}

# =============================================================================
# Verification
# =============================================================================
verify_installation() {
    info "Verifying installation..."
    local all_ok=true

    # Check Python
    if ! find_python; then
        error "  ✗ Python >= $PYTHON_MIN_VERSION"
        all_ok=false
    else
        success "  ✓ Python $PYTHON_VERSION"
    fi

    # Check pip packages
    for pkg in "${REQUIRED_PIP_PACKAGES[@]}"; do
        if "$PYTHON_CMD" -c "import importlib; importlib.import_module('${pkg/pyyaml/yaml}')" &>/dev/null; then
            success "  ✓ $pkg"
        else
            error "  ✗ $pkg"
            all_ok=false
        fi
    done

    # Check Playwright Chromium
    if "$PYTHON_CMD" -c "
from playwright.sync_api import sync_playwright
from pathlib import Path
with sync_playwright() as pw:
    p = Path(pw.chromium.executable_path)
    assert p.is_file()
" &>/dev/null; then
        success "  ✓ Playwright Chromium"
    else
        error "  ✗ Playwright Chromium"
        all_ok=false
    fi

    # Check Java (optional)
    if [[ "$MINIMAL" == false ]]; then
        if command -v java &>/dev/null; then
            success "  ✓ Java (PlantUML support)"
        else
            warn "  ○ Java not available (PlantUML diagrams won't render)"
        fi
    fi

    echo ""
    if [[ "$all_ok" == true ]]; then
        success "═══════════════════════════════════════════════════"
        success " BookBinder is ready!"
        success " Run: $PYTHON_CMD $SCRIPT_DIR/make_a_book.py BOOK.md"
        success "═══════════════════════════════════════════════════"
    else
        die "Some components failed to install. See errors above."
    fi
}

# =============================================================================
# Main
# =============================================================================
main() {
    echo ""
    info "═══════════════════════════════════════════════════"
    info " BookBinder Bootstrap"
    info "═══════════════════════════════════════════════════"
    echo ""

    detect_os
    ensure_python
    ensure_pip
    install_python_deps
    install_playwright_chromium

    if [[ "$MINIMAL" == false ]]; then
        ensure_java
    fi

    echo ""
    verify_installation
}

main "$@"