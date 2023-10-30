import os
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