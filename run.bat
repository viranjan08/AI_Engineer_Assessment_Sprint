@echo off
echo Starting DOTMappers AI Engineer Project...
echo.

IF NOT EXIST "venv" (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat
echo Installing/Verifying dependencies...
pip install -r requirements.txt

echo.
echo Starting FastAPI Backend (Port 8000)...
start /b cmd /c "uvicorn app.main:app --host 127.0.0.1 --port 8000"

echo.
echo Starting Streamlit Frontend (Port 8501)...
start /b cmd /c "streamlit run ui\app.py --server.port 8501 --server.headless true"

echo.
echo ========================================================
echo All services launched!
echo API Documentation: http://localhost:8000/docs
echo Streamlit UI:      http://localhost:8501
echo ========================================================
echo Close this window or press Ctrl+C to stop.
