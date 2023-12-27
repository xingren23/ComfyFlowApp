import os
from loguru import logger
import streamlit as st
from enum import Enum

# enum app status
class AppStatus(Enum):
    CREATED = "Created"
    PREVIEWED = "Previewed"
    PUBLISHED = "Published"
    RUNNING = "Running"
    STARTED = "Started"
    STOPPING = "Stopping"
    STOPPED = "Stopped"
    INSTALLING = "Installing"
    INSTALLED = "Installed"
    UNINSTALLED = "Uninstalled"
    ERROR = "Error"


@st.cache_resource
def get_workspace_model():
    logger.debug("get_workspace_instance")
    from modules.workspace_model import WorkspaceModel
    sqliteInstance = WorkspaceModel()
    return sqliteInstance

@st.cache_resource
def get_myapp_model():
    logger.debug("get_myapp_model")
    from modules.myapp_model import MyAppModel
    myapp_model = MyAppModel()
    return myapp_model 

@st.cache_resource
def get_comfy_client():
    logger.debug("get_comfy_client")
    from modules.comfyclient import ComfyClient
    server_addr = os.getenv('COMFYUI_SERVER_ADDR')
    comfy_client = ComfyClient(server_addr=server_addr)
    return comfy_client

def check_comfyui_alive():
    try:
        get_comfy_client().queue_remaining()
        return True
    except Exception as e:
        logger.warning(f"check comfyui alive error, {e}")
        return False    

@st.cache_data(ttl=60)
def get_comfyui_object_info():
    logger.debug("get_comfy_object_info")
    comfy_client = get_comfy_client()
    comfy_object_info = comfy_client.get_node_class()
    return comfy_object_info


def get_comfyflow_token():
    import extra_streamlit_components as stx
    cookie_manager = stx.CookieManager("token")
    token = cookie_manager.get('comfyflow_token')
    return token