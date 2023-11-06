import os
from loguru import logger
import streamlit as st
import extra_streamlit_components as stx

@st.cache_resource
def get_sqlite_instance():
    logger.debug("get_sqlite_instance")
    from modules.sqlitehelper import SQLiteHelper
    sqliteInstance = SQLiteHelper()      
    return sqliteInstance

@st.cache_resource
def get_comfy_client():
    logger.debug("get_comfy_client")
    from modules.comfyclient import ComfyClient
    server_addr = os.getenv('COMFYUI_SERVER_ADDR', default='localhost:8188')
    comfy_client = ComfyClient(server_addr=server_addr)
    return comfy_client

def get_auth_instance():
    logger.debug("get auth_instance")
    from modules.authenticate import MyAuthenticate
    auth_instance =  MyAuthenticate("comfyflow_token", "ComfyFlowApp： Load ComfyUI workflow as webapp in seconds.")
    return auth_instance