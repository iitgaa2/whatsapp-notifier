#!/bin/bash
# Quick Start Script for WhatsApp Automation with uv

set -e

echo "🚀 WhatsApp Automation Quick Start"
echo "=================================="

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        # Windows
        powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    else
        # macOS/Linux
        curl -LsSf https://astral.sh/uv/install.sh | sh
    fi
    
    # Reload PATH
    export PATH="$HOME/.cargo/bin:$PATH"
    echo "✅ uv installed successfully"
else
    echo "✅ uv is already installed"
fi

# Install dependencies
echo "📦 Installing dependencies..."
uv sync

# Check Tesseract
echo "🔍 Checking Tesseract OCR..."
if ! command -v tesseract &> /dev/null; then
    echo "⚠️  Tesseract OCR not found!"
    echo "📖 Please install Tesseract:"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "   brew install tesseract"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "   sudo apt-get install tesseract-ocr"
    else
        echo "   Download from: https://github.com/UB-Mannheim/tesseract/wiki"
    fi
    echo ""
    echo "⚠️  You can continue without Tesseract, but OCR won't work."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ Tesseract OCR found"
fi

# Run setup verification
echo "🧪 Running setup verification..."
uv run python setup.py

echo ""
echo "🎉 Setup complete!"
echo ""
echo "🚀 To start the WhatsApp automation:"
echo "   uv run python main.py --interactive"
echo ""
echo "📖 For help:"
echo "   uv run python main.py --help"
echo "" 