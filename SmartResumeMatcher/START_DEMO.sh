#!/bin/bash
echo "============================================"
echo "   SMART RESUME MATCHER - MINI PROJECT"
echo "============================================"
echo ""
echo "[1] Installing dependencies..."
pip install -r requirements.txt
echo ""
echo "[2] Launching Backend API..."
# Run uvicorn in the background
nohup python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
echo "[OK] Backend started on port 8000"
echo ""
echo "[3] Launching Streamlit app..."
echo "============================================"
sleep 2
python -m streamlit run app.py --server.port 8501 --server.headless true
