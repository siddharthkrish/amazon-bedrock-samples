#!/bin/bash
# Quick setup script for the Bedrock Claude CLI

echo "==================================="
echo "Bedrock Claude CLI Setup"
echo "==================================="
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed."
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "✅ uv installed. Please restart your shell and run this script again."
    exit 0
fi

echo "✅ uv is installed"
echo ""

# Install dependencies
echo "Installing dependencies..."
uv pip install -e .

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Installation complete!"
    echo ""
    echo "Usage examples:"
    echo "  bedrock-claude -p prompt.txt"
    echo "  bedrock-claude -p prompt.txt -f image.png -f document.pdf"
    echo ""
    echo "For more information, see README.md"
else
    echo "❌ Installation failed"
    exit 1
fi
