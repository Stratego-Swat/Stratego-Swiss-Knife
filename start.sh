#!/bin/bash
# Stratego Swiss Knife - Start Script
# Avvia entrambi i server: Login (8000) e SEO App (8001)

echo "🚀 Starting Stratego Swiss Knife..."
echo ""

# Kill existing processes
echo "🔄 Stopping existing servers..."
pkill -f "uvicorn.*8000" 2>/dev/null
pkill -f "uvicorn.*8001" 2>/dev/null
sleep 1

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment
source .venv/bin/activate

# Start SEO App on port 8001 in background
echo "📦 Starting SEO Content Agent on port 8001..."
cd apps/seo_content_agent
python -m uvicorn web.main:app --host 0.0.0.0 --port 8001 --reload &
SEO_PID=$!
cd ../..

sleep 2

# Start Login/Dashboard on port 8000
echo "🔐 Starting Stratego Swiss Knife on port 8000..."
cd Login
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
LOGIN_PID=$!
cd ..

echo ""
echo "✅ All servers started!"
echo ""
echo "📍 Access Points:"
echo "   🔐 Login:     http://localhost:8000"
echo "   📦 SEO App:   http://localhost:8001"
echo ""
echo "👤 Credentials:"
echo "   Username: admin"
echo "   Password: Stratego"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for interrupt
trap "echo ''; echo '🛑 Stopping servers...'; kill $SEO_PID $LOGIN_PID 2>/dev/null; exit 0" INT
wait
