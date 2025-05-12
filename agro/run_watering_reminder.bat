@echo off
:: Path to your Python executable (in your virtual environment)
SET PYTHON_PATH="C:\Users\RUDRA PATEL\PycharmProjects\AGRO_BUILD_final 1\venv\Scripts\python.exe"

:: Path to your manage.py
SET MANAGE_PY="C:\Users\RUDRA PATEL\PycharmProjects\AGRO_BUILD_final 1\agro\manage.py"

:: Path to the log file
SET LOG_FILE="C:\Users\RUDRA PATEL\PycharmProjects\AGRO_BUILD_final 1\agro\watering.log"

:: Run the command and log output
%PYTHON_PATH% %MANAGE_PY% send_watering_reminder >> %LOG_FILE% 2>&1