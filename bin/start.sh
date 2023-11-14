#!/bin/bash

# get current path
CUR_DIR="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
PROJECT_PATH=$(dirname $(dirname "$CUR_DIR"))
echo "$PROJECT_PATH"
cd $PROJECT_PATH

# set LOGURU_LEVEL to ERROR
export LOGURU_LEVEL=INFO
export DISCORD_CLIENT_ID=1163088920305737728
export DISCORD_CLIENT_SECRET=hdqis8gZ9YVvvM-qxAbYApd6ai40nBlk
export REDIRECT_URI=http://localhost:8501

export COMFYFLOW_API_URL=https://api.comfyflow.com
export COMFYUI_SERVER_ADDR=localhost:8188
export INNER_COMFYUI_SERVER_ADDR=localhost:9188

# app name
APP_NAME="Home"
# script params
nohup streamlit run "$APP_NAME.py" > home.log 2>&1 &

echo "Starting $APP_NAME..."