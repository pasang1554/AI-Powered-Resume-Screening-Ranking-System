@echo off
title Smart Resume Matcher - Mini Project Demo
color 0A
echo.
echo  ============================================
echo     SMART RESUME MATCHER - MINI PROJECT
echo  ============================================
echo.
echo  [1] Starting application...
echo.
pip install -r requirements.txt > nul 2>&1
echo  [OK] Dependencies installed
echo.
echo  [2] Launching Backend API...
start "Backend API" python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
echo  [OK] Backend started on port 8000
echo.
echo  [3] Launching Streamlit app...
echo.
echo  ============================================
echo  APP WILL OPEN AUTOMATICALLY IN BROWSER
echo  ============================================
echo.
timeout /t 2 > nul
python -m streamlit run app.py --server.port 8501 --server.headless true
pause
