@echo off
setlocal

:: get current directory
set CUR_DIR=%~dp0
set PROJECT_DIR=%CUR_DIR%..\

cd /d %PROJECT_DIR%

:: make mklink comfyflow.db manager/comfyflow.db
mklink comfyflow.db manager/comfyflow.db
mklink /d .streamlit manager/.streamlit
mklink /d public manager/public
mklink /d models manager/models

:: start server
streamlit run Home.py

endlocal