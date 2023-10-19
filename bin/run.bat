@echo off
setlocal

:: get current directory
set CUR_DIR=%~dp0
set PROJECT_DIR=%CUR_DIR%..\
cd /d %PROJECT_DIR%

:: start server
streamlit run Home.py

endlocal