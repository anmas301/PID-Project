#!/bin/bash
# Quick start script untuk menjalankan pipeline

echo "🌫️ ISPA Risk Monitoring Pipeline - Quick Start"
echo "=============================================="
echo ""

# Check Python
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.8+"
    exit 1
fi

echo "✓ Python found: $(python --version)"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate venv
echo "🔧 Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "✓ Setup complete!"
echo ""
echo "Choose an option:"
echo "1. Run full pipeline"
echo "2. Run pipeline without model training"
echo "3. Launch dashboard only"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo "🚀 Running full pipeline..."
        python src/main.py
        ;;
    2)
        echo "🚀 Running pipeline without model training..."
        python src/main.py --skip-model
        ;;
    3)
        echo "🎨 Launching dashboard..."
        streamlit run src/dashboard.py
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "✓ Done!"
