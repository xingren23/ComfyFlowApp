#!/bin/bash

# get current path
CUR_DIR="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
PROJECT_PATH=$(dirname $(dirname "$CUR_DIR"))
echo "$PROJECT_PATH"
cd $PROJECT_PATH

# mklink
if [ -e "manager/comfyflow.db" ]; then
    echo "manager/comfyflow.db is exist"
else
    echo "ln -s comfyflow.db manager/comfyflow.db"
    ln -s comfyflow.db manager/comfyflow.db

if [ -e "manager/.streamlit" ]; then
    echo "manager/.streamlit is exist"
else
    echo "ln -s .streamlit manager/.streamlit"
    ln -s .streamlit manager/.streamlit

if [ -e "manager/public" ]; then
    echo "manager/public is exist"
else
    echo "ln -s public manager/public"
    ln -s public manager/public

if [ -e "manager/mod" ]; then    
    echo "manager/models is exist"
else
    echo "ln -s models manager/models"
    ln -s models manager/models

# app name
APP_NAME="Home"
# script params
nohup streamlit run "$APP_NAME.py" > app.log 2>&1 &

echo "Starting $APP_NAME..."