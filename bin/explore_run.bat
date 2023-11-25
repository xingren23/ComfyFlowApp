@echo off
setlocal

:: get current directory
set CUR_DIR=%~dp0
set PROJECT_DIR=%CUR_DIR%..\
cd /d %PROJECT_DIR%

:: set LOGURU_LEVEL to INFO
set LOGURU_LEVEL=INFO
set STREAMLIT_SERVER_PORT=8503
:: set COMFYFLOW_API_URL to https://api.comfyflow.app
set COMFYFLOW_API_URL=https://api.comfyflow.app
:: set COMFYUI_SERVER_ADDR to localhost:8288
set COMFYUI_SERVER_ADDR=http://localhost:8288
:: set INNER_COMFYUI_SERVER_ADDR to localhost:9288
set INNER_COMFYUI_SERVER_ADDR=http://localhost:9288
:: set MODE
set MODE=Explore

:: start server
python -m streamlit run Home.py
pause
endlocal