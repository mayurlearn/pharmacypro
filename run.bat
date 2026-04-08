@echo off
title Pharmacy Management System
echo.
echo  =============================================
echo   Pharmacy Management System - Starting...
echo  =============================================
echo.
cd /d "%~dp0"
call ..\..\.venv\Scripts\activate.bat 2>nul || call ..\.venv\Scripts\activate.bat 2>nul

where streamlit >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing dependencies...
    pip install -r requirements.txt -q
)

echo Starting server at http://localhost:8501
echo Press CTRL+C to stop the application.
echo.
start "" http://localhost:8501
streamlit run app.py --server.headless=true --server.port=8501
pause
