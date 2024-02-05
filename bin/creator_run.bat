@echo off
setlocal

:: get current directory
set CUR_DIR=%~dp0
set PROJECT_DIR=%CUR_DIR%..\
cd /d %PROJECT_DIR%

:: set LOGURU_LEVEL to INFO
set LOGURU_LEVEL=INFO

set STREAMLIT_SERVER_PORT=8501
:: set COMFYFLOW_API_URL to https://api.comfyflow.app
set COMFYFLOW_API_URL=https://api.comfyflow.app
:: set COMFYUI_SERVER_ADDR to localhost:8188
set COMFYUI_SERVER_ADDR=http://localhost:8188
:: set MODE
set MODE=Creator

:: start server
python -m streamlit run Home.py
pause
endlocal