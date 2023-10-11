#!/bin/bash

# app name
APP_NAME="comfyflowapp"
# script params
SCRIPT_PARAMS=" --server_addr 192.168.1.11:8188 --workflow sdxl_basic"
nohup streamlit run "$APP_NAME.py" " -- $SCRIPT_PARAMS" > app.log 2>&1 &