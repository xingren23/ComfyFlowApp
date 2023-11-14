@echo off
setlocal

:: get current directory
set CUR_DIR=%~dp0
set PROJECT_DIR=%CUR_DIR%..\
cd /d %PROJECT_DIR%

:: set LOGURU_LEVEL to INFO
set LOGURU_LEVEL=INFO
set DISCORD_CLIENT_ID=1163088920305737728
set DISCORD_CLIENT_SECRET=hdqis8gZ9YVvvM-qxAbYApd6ai40nBlk
set REDIRECT_URI=http://localhost:8501

set COMFYFLOW_API_URL=https://api.comfyflow.app
set COMFYUI_SERVER_ADDR=localhost:8188
set INNER_COMFYUI_SERVER_ADDR=localhost:9188

:: start server
streamlit run Home.py

endlocal