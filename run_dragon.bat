@echo off
title Dragon AI Core 2.0 - Autonomous Desktop Companion
cd /d "%~dp0"
echo ====================================================
echo         STARTING DRAGON AI CORE v2.0
echo ====================================================
echo.
if exist "envDragon\Scripts\python.exe" (
    "envDragon\Scripts\python.exe" -u main.py
) else (
    python -u main.py
)
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Dragon exited with error code %ERRORLEVEL%.
    pause
)
