#!/bin/bash

# get current path
CUR_DIR="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
PROJECT_PATH=$(dirname $(dirname "$CUR_DIR"))
echo "$PROJECT_PATH"
cd $PROJECT_PATH

# set LOGURU_LEVEL to ERROR
export LOGURU_LEVEL=INFO
# set COMFYFLOW_API_URL to comfyflow api url
export COMFYFLOW_API_URL=https://api.comfyflow.app
# set COMFYUI_SERVER_ADDR to comfyui server addr
export COMFYUI_SERVER_ADDR=localhost:8188
# set INNER_COMFYUI_SERVER_ADDR to inner comfyui server addr
export INNER_COMFYUI_SERVER_ADDR=localhost:9188
# set MODE to Studio
export MODE=Studio

# app name
APP_NAME="Home"
# script params
python -m streamlit run "$APP_NAME.py"