#!/bin/bash
# Scribe Repository Setup Script
# Run this after cloning to initialize your development environment

echo "🎯 Setting up Scribe development environment..."
echo ""

# Check Python version
python_version=$(python --version 2>&1 | grep -oP '(?<=Python )\d+\.\d+')
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.9+ required. You have Python $python_version"
    exit 1
fi

echo "✅ Python $python_version detected"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Upgrade pip
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating data directories..."
mkdir -p data/{audio,logs,analytics,sessions,metrics}
mkdir -p docs/screenshots
mkdir -p models

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Quick start:"
echo "   1. Activate venv:"
echo "      Windows: venv\\Scripts\\activate"
echo "      Linux/Mac: source venv/bin/activate"
echo "   2. Run Scribe: python run_scribe.py"
echo ""
echo "📖 See DEPLOYMENT_GUIDE.md for publishing to GitHub"
