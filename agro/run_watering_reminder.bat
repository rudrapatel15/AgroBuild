@echo off
:: Path to your Python executable (in your virtual environment)
SET PYTHON_PATH="C:\Users\a\Desktop\Agro Build Pro\AgroBuild\venv\Scripts\python.exe"

:: Path to your manage.py
SET MANAGE_PY="C:\Users\a\Desktop\Agro Build Pro\AgroBuild\agro\manage.py"

:: Path to the log file
SET LOG_FILE="C:\Users\a\Desktop\Agro Build Pro\AgroBuild\agro\watering.log"

:: Run the command and log output
%PYTHON_PATH% %MANAGE_PY% send_watering_reminder >> %LOG_FILE% 2>&1