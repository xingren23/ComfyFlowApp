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
    logger.info("get_workspace_instance")
    from modules.workspace_model import WorkspaceModel
    sqliteInstance = WorkspaceModel()
    return sqliteInstance

@st.cache_resource
def get_myapp_model():
    logger.info("get_myapp_model")
    from modules.myapp_model import MyAppModel
    myapp_model = MyAppModel()
    return myapp_model 

@st.cache_resource
def get_comfy_client():
    logger.info("get_comfy_client")
    from modules.comfyclient import ComfyClient
    server_addr = os.getenv('COMFYUI_SERVER_ADDR', default='localhost:8188')
    comfy_client = ComfyClient(server_addr=server_addr)
    return comfy_client


@st.cache_data(ttl=60)
def get_local_object_info():
    logger.info("get_comfy_object_info")
    comfy_client = get_comfy_client()
    comfy_object_info = comfy_client.get_node_class()
    return comfy_object_info


def get_auth_instance():
    logger.debug("get auth_instance")
    from modules.authenticate import MyAuthenticate
    auth_instance =  MyAuthenticate("comfyflow_token", "ComfyFlowApp： Load ComfyUI workflow as webapp in seconds.")
    return auth_instance

