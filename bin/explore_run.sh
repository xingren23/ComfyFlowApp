#!/bin/bash

# get current path
CUR_DIR="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
PROJECT_PATH=$(dirname $(dirname "$CUR_DIR"))
echo "$PROJECT_PATH"
cd $PROJECT_PATH

# set LOGURU_LEVEL to ERROR
export LOGURU_LEVEL=INFO

export STREAMLIT_SERVER_PORT=8503
# set COMFYFLOW_API_URL to comfyflow api url
export COMFYFLOW_API_URL=https://api.comfyflow.app

# set discord callback url
export DISCORD_REDIRECT_URI=http://localhost:8503
# set MODE to Studio
export MODE=Explore

# app name
APP_NAME="Home"
# script params
nohup python -m streamlit run "$APP_NAME.py" > explore.log 2>&1 &