#!/bin/bash

# get current path
CUR_DIR="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
PROJECT_PATH=$(dirname $(dirname "$CUR_DIR"))
echo "$PROJECT_PATH"
cd $PROJECT_PATH

# set LOGURU_LEVEL to ERROR
export LOGURU_LEVEL=DEBUG

# app name
APP_NAME="Apps"
# script params
nohup streamlit run "$APP_NAME.py" > app.log 2>&1 &

echo "Starting $APP_NAME..."