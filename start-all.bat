@echo off
echo Starting PhilEarthStats (Backend + Frontend)...
echo.

start "PhilEarthStats Backend" cmd /k call start-backend.bat
timeout /t 3 /nobreak >nul
start "PhilEarthStats Frontend" cmd /k call start-frontend.bat

echo.
echo Both servers are starting in separate windows...
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Close this window or press any key to continue...
pause >nul
