#!/bin/bash
# Quick setup script for the Bedrock Claude CLI

echo "==================================="
echo "Bedrock Claude CLI Setup"
echo "==================================="
echo ""

# Require uv to manage dependencies
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
