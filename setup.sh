#!/bin/bash
# Setup script for travelTools

set -e

echo "🌴 Travel Tools Setup"
echo "===================="

# Check Python version
echo ""
echo "Checking Python version..."
if ! command -v python3.11 &> /dev/null; then
    echo "❌ Python 3.11+ is required but not found"
    echo "Please install Python 3.11 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3.11 --version)
echo "✓ Found: $PYTHON_VERSION"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠ Virtual environment already exists, skipping"
else
    python3.11 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip install --upgrade pip > /dev/null
pip install -e . > /dev/null
echo "✓ Installed travel-tools package"

pip install -r requirements-dev.txt > /dev/null
echo "✓ Installed development dependencies"

# Install Playwright
echo ""
echo "Installing Playwright browsers..."
playwright install chromium > /dev/null 2>&1
echo "✓ Playwright Chromium installed"

# Verify installation
echo ""
echo "Verifying installation..."
if python -m travel_tools.launcher --help > /dev/null 2>&1; then
    echo "✓ travel-tools command works"
else
    echo "❌ travel-tools command failed"
    exit 1
fi

# Setup complete
echo ""
echo "===================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Copy your package data:"
echo "   mkdir -p data/cancun/transat/raw"
echo "   cp /path/to/packages.json data/cancun/transat/raw/"
echo ""
echo "3. Run the pipeline:"
echo "   python -m travel_tools.launcher"
echo ""
echo "For more info, see:"
echo "  - README.md (full documentation)"
echo "  - QUICKSTART.md (quick guide)"
echo ""
