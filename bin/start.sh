#!/bin/bash

# app name
APP_NAME="🏠_Home"
# script params
nohup streamlit run "$APP_NAME.py" > app.log 2>&1 &