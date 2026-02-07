#!/bin/bash

echo "🎓 NextStep - Installation Script"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Found Python $python_version"
echo ""

# Create virtual environment (recommended)
echo "Would you like to create a virtual environment? (recommended)"
read -p "Enter y/n: " create_venv

if [ "$create_venv" = "y" ] || [ "$create_venv" = "Y" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
    echo ""
    echo "To activate it, run:"
    echo "  source venv/bin/activate  (Mac/Linux)"
    echo "  venv\\Scripts\\activate     (Windows)"
    echo ""
fi

# Install dependencies
echo "Installing dependencies..."
if [ "$create_venv" = "y" ] || [ "$create_venv" = "Y" ]; then
    source venv/bin/activate 2>/dev/null || true
fi

pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Set up environment variables
if [ ! -f .env ]; then
    echo "Setting up environment variables..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your GEMINI_API_KEY"
    echo "   Get a free key from: https://aistudio.google.com/app/apikey"
    echo "   (Optional - app works without AI features)"
else
    echo "✅ .env file already exists"
fi
echo ""

# Test the backend
echo "Testing backend..."
python test_backend.py
echo ""

# Final instructions
echo "=================================="
echo "🎉 Installation Complete!"
echo "=================================="
echo ""
echo "To run the application:"
echo "  1. streamlit run app.py"
echo "  2. Open browser to http://localhost:8501"
echo ""
echo "For AI features (optional):"
echo "  1. Get API key from https://aistudio.google.com/app/apikey"
echo "  2. Add to .env file: GEMINI_API_KEY=your_key"
echo "  3. Restart the app"
echo ""
echo "Happy career planning! 🚀"
