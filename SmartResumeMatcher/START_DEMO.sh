streamlit run app.py#!/bin/bash
echo "============================================"
echo "   SMART RESUME MATCHER - MINI PROJECT"
echo "============================================"
echo ""
echo "[1] Installing dependencies..."
pip install -r requirements.txt
echo ""
echo "[2] Launching Streamlit app..."
echo "============================================"
streamlit run app.py --server.port 8501 --server.headless true
