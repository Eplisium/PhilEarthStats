@echo off
echo Starting PhilEarthStats Backend...
echo.

cd backend

if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing/Updating dependencies...
pip install -r requirements.txt

echo.
echo Starting Flask server...
echo Backend will be available at http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
