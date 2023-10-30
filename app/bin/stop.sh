#!/bin/bash

# app name
APP_NAME="Apps"

# 查找并终止正在运行的 Flask 应用程序进程
PID=$(ps aux | grep "$APP_NAME" | grep -v grep | awk '{print $2}')
if [ -n "$PID" ]; then
    echo "Stopping $APP_NAME $PID..."
    kill $PID
    echo "Stoped $APP_NAME"
else
    echo "$APP_NAME is not running."
fi