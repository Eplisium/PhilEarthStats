@echo off
echo Starting PhilEarthStats Frontend...
echo.

cd frontend

if not exist "node_modules\" (
    echo Installing dependencies...
    npm install
)

echo.
echo Starting development server...
echo Frontend will be available at http://localhost:3000
echo Press Ctrl+C to stop the server
echo.

npm run dev -- --host

pause
