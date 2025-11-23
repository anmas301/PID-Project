#!/bin/bash
# Quick Public Access menggunakan Ngrok

echo "🚀 Setting up public access for dashboard..."
echo ""

# Check if streamlit is running
if pgrep -f "streamlit run" > /dev/null; then
    echo "✅ Streamlit dashboard already running"
else
    echo "📊 Starting Streamlit dashboard..."
    streamlit run src/dashboard.py --server.port 8501 &
    sleep 5
fi

echo ""
echo "🌐 Creating public URL with Ngrok..."
echo ""
echo "IMPORTANT: You need ngrok installed and configured!"
echo "1. Download: https://ngrok.com/download"
echo "2. Signup: https://dashboard.ngrok.com/signup"
echo "3. Get auth token: https://dashboard.ngrok.com/get-started/your-authtoken"
echo "4. Run: ngrok config add-authtoken YOUR_TOKEN"
echo ""
read -p "Press Enter when ngrok is ready, or Ctrl+C to cancel..."

# Start ngrok
echo ""
echo "🔗 Starting ngrok tunnel..."
ngrok http 8501
