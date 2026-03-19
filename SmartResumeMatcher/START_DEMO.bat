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
echo  [2] Launching Streamlit app...
echo.
echo  ============================================
echo  APP WILL OPEN AUTOMATICALLY IN BROWSER
echo  ============================================
echo.
timeout /t 2 > nul
streamlit run app.py --server.port 8501 --server.headless true
pause
