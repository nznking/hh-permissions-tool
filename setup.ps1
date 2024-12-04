# Setup script for HH Permissions Tool (Windows)
#Requires -Version 5.0

$ErrorActionPreference = "Stop"
$MIN_PYTHON_VERSION = "3.9.0"
$POETRY_VERSION = "1.7.1"

function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Test-Command($CommandName) {
    return $null -ne (Get-Command $CommandName -ErrorAction SilentlyContinue)
}

function Compare-Versions($Version1, $Version2) {
    $v1 = [version]$Version1
    $v2 = [version]$Version2
    return $v1.CompareTo($v2)
}

Write-ColorOutput Green "🔍 Checking prerequisites for HH Permissions Tool..."

# Check Python installation
if (-not (Test-Command "python")) {
    Write-ColorOutput Red "❌ Python is not installed! Please install Python $MIN_PYTHON_VERSION or later from https://python.org"
    exit 1
}

$pythonVersion = (python -c "import sys; print('.'.join(map(str, sys.version_info[:3])))")
if ((Compare-Versions $pythonVersion $MIN_PYTHON_VERSION) -lt 0) {
    Write-ColorOutput Red "❌ Python version $pythonVersion is too old. Please install Python $MIN_PYTHON_VERSION or later."
    exit 1
}

Write-ColorOutput Green "✅ Python $pythonVersion found"

# Check Poetry installation
if (-not (Test-Command "poetry")) {
    Write-ColorOutput Yellow "📦 Poetry not found. Installing Poetry..."
    try {
        (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
    }
    catch {
        Write-ColorOutput Red "❌ Failed to install Poetry: $_"
        exit 1
    }
}

$poetryVersion = (poetry --version).Split(" ")[-1]
Write-ColorOutput Green "✅ Poetry $poetryVersion found"

# Configure Poetry to create virtual environment in project directory
Write-ColorOutput Yellow "⚙️ Configuring Poetry..."
poetry config virtualenvs.in-project true

# Install dependencies
Write-ColorOutput Yellow "📦 Installing project dependencies..."
try {
    poetry install
}
catch {
    Write-ColorOutput Red "❌ Failed to install dependencies: $_"
    exit 1
}

Write-ColorOutput Green "✅ Dependencies installed successfully"

# Create .env file if it doesn't exist
if (-not (Test-Path .env)) {
    Write-ColorOutput Yellow "📝 Creating .env file from template..."
    Copy-Item .env.example .env
    Write-ColorOutput Green "✅ Created .env file. Please update it with your settings."
}

Write-ColorOutput Green "✨ Setup completed successfully!"
Write-ColorOutput Cyan @"

🚀 To start using HH Permissions Tool:
1. Update the .env file with your Google Cloud credentials
2. Run: poetry shell
3. Then: python -m hh_permissions_tool.cli --help

For more information, see the README.md file.
"@
