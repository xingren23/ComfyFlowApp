import os
import requests
from loguru import logger
import streamlit as st


@st.cache_resource
def get_sqlite_instance():
    logger.info("get_sqlite_instance")
    from modules.sqlitehelper import SQLiteHelper
    sqliteInstance = SQLiteHelper()      
    return sqliteInstance

@st.cache_resource
def get_comfy_client():
    logger.info("get_comfy_client")
    from modules.comfyclient import ComfyClient
    server_addr = os.getenv('COMFYUI_SERVER_ADDR', default='localhost:8188')
    comfy_client = ComfyClient(server_addr=server_addr)
    return comfy_client

@st.cache_data(ttl=3600)
def get_comfyflow_apps():
    logger.info("get_comfyflow_apps")
    # get apps from comfyflow.app
    comfyflow_api = os.getenv(
        'COMFYFLOW_API_URL', default='http://localhost:8787')
    comfyflow_api_token = os.getenv(
        'COMFYFLOW_API_TOKEN', default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9')
    headers = {"Authorization": f"Bearer {comfyflow_api_token}"}
    ret = requests.get(f"{comfyflow_api}/api/app/all", headers=headers)
    if ret.status_code != 200:
        logger.error(f"get_comfyflow_apps failed, {ret}")
        return None
    else:
        return ret.json()
    