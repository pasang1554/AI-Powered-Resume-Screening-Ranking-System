#!/bin/bash
echo "============================================"
echo "   SMART RESUME MATCHER - v8.1.12"
echo "============================================"
echo ""

# [0] Pre-flight Check: Environment Validation
if [ ! -f .env ]; then
    echo "[ERROR] .env file not found!"
    echo "Please create a .env file based on .env.example with your GROQ_API_KEY."
    exit 1
fi

if ! grep -q "GROQ_API_KEY" .env; then
    echo "[ERROR] GROQ_API_KEY missing in .env!"
    echo "Please add your API key to the .env file to enable AI features."
    exit 1
fi

echo "[1] Checking dependencies..."
if [[ "$1" == "-f" ]]; then
    pip3 install -r requirements.txt
else
    echo "Skipping installation (use ./START_DEMO.sh -f for fresh install)"
fi
echo ""

# [2] Infrastructure Cleanup
echo "[2] Orchestrating Backend & Frontend..."
lsof -ti:8000 | xargs kill -9 > /dev/null 2>&1
lsof -ti:8501 | xargs kill -9 > /dev/null 2>&1
echo "[OK] Cleaned up existing processes on ports 8000 & 8501."
echo ""

echo "[3] Launching Universal Talent Singularity..."
# Run uvicorn in the background
nohup python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
echo "[OK] Backend API Active on :8000"
echo ""

sleep 2
echo "Launching Dashboard..."
echo "============================================"
python3 -m streamlit run app.py --server.port 8501 --server.headless true
