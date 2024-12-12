#!/usr/bin/env bash

# Setup script for HH Permissions Tool (Unix/Linux/macOS)
set -e

# Constants
MIN_PYTHON_VERSION="3.9.0"
POETRY_VERSION="1.7.1"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to compare version numbers
version_compare() {
    if [[ $1 == $2 ]]; then
        return 0
    fi
    local IFS=.
    local i ver1=($1) ver2=($2)
    for ((i=${#ver1[@]}; i<${#ver2[@]}; i++)); do
        ver1[i]=0
    done
    for ((i=0; i<${#ver1[@]}; i++)); do
        if [[ -z ${ver2[i]} ]]; then
            ver2[i]=0
        fi
        if ((10#${ver1[i]} > 10#${ver2[i]})); then
            return 1
        fi
        if ((10#${ver1[i]} < 10#${ver2[i]})); then
            return 2
        fi
    done
    return 0
}

# Function to check command existence
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo -e "${GREEN}🔍 Checking prerequisites for HH Permissions Tool...${NC}"

# Check Python installation
if ! command_exists python3; then
    echo -e "${RED}❌ Python is not installed! Please install Python $MIN_PYTHON_VERSION or later${NC}"
    exit 1
fi

# Get Python version
PYTHON_VERSION=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:3])))")
version_compare "$PYTHON_VERSION" "$MIN_PYTHON_VERSION"
if [[ $? == 2 ]]; then
    echo -e "${RED}❌ Python version $PYTHON_VERSION is too old. Please install Python $MIN_PYTHON_VERSION or later${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"

# Check pip installation
if ! command_exists pip3; then
    echo -e "${YELLOW}📦 Installing pip...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
        python3 get-pip.py
        rm get-pip.py
    else
        sudo apt-get update && sudo apt-get install -y python3-pip
    fi
fi

# Check Poetry installation
if ! command_exists poetry; then
    echo -e "${YELLOW}📦 Poetry not found. Installing Poetry...${NC}"
    curl -sSL https://install.python-poetry.org | python3 -
    
    # Add Poetry to PATH for the current session
    export PATH="$HOME/.local/bin:$PATH"
fi

POETRY_PATH=$(command -v poetry)
echo -e "${GREEN}✅ Poetry found at: $POETRY_PATH${NC}"

# Configure Poetry to create virtual environment in project directory
echo -e "${YELLOW}⚙️ Configuring Poetry...${NC}"
poetry config virtualenvs.in-project true

# Install dependencies
echo -e "${YELLOW}📦 Installing project dependencies...${NC}"
poetry install

# Create .env file if it doesn't exist
if [[ ! -f .env ]]; then
    echo -e "${YELLOW}📝 Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ Created .env file. Please update it with your settings.${NC}"
fi

echo -e "${GREEN}✨ Setup completed successfully!${NC}"
echo -e "${CYAN}
🚀 To start using HH Permissions Tool:
1. Update the .env file with your Google Cloud credentials
2. Run: poetry shell
3. Then: python -m hh_permissions_tool.cli --help

For more information, see the README.md file.${NC}"
