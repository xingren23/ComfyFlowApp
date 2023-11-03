import os
from loguru import logger
import requests
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


@st.cache_data(ttl=60)
def get_local_object_info():
    logger.info("get_comfy_object_info")
    comfy_client = get_comfy_client()
    comfy_object_info = comfy_client.get_node_class()
    return comfy_object_info


@st.cache_data(ttl=3600)
def get_comfyflow_object_info():
    comfyflow_api = os.getenv(
        'COMFYFLOW_API_URL', default='http://localhost:8787')
    # request comfyflow object info
    object_info = requests.get(f"{comfyflow_api}/api/comfyflow/object_info")
    if object_info.status_code != 200:
        logger.error("get_comfyflow_object_info failed")
        return None
    logger.info(f"get_comfyflow_object_info, {object_info}")
    return object_info.json()


@st.cache_data(ttl=3600)
def get_comfyflow_model_info():
    comfyflow_api = os.getenv(
        'COMFYFLOW_API_URL', default='http://localhost:8787')
    # request comfyflow object info
    model_info = requests.get(f"{comfyflow_api}/api/comfyflow/model_info")
    if model_info.status_code != 200:
        logger.error("get_comfyflow_model_info failed")
        return None
    logger.info(f"get_comfyflow_model_info, {model_info}")
    return model_info.json()


def publish_app(name, description, image, app_conf, api_conf, template, status):
    
    comfyflow_api = os.getenv(
        'COMFYFLOW_API_URL', default='http://localhost:8787')
    # post app to comfyflow.app
    app = {
        "name": name,
        "description": description,
        "image": image,
        "app_conf": app_conf,
        "api_conf": api_conf,
        "template": template,
        "status": status
    }
    logger.debug(f"publish app to comfyflow.app, {app}")
    comfyflow_api_token = os.getenv(
        'COMFYFLOW_API_TOKEN', default='')
    # Authorization header
    headers = {"Authorization": f"Bearer {comfyflow_api_token}"}
    ret = requests.post(f"{comfyflow_api}/api/app/publish", json=app, headers=headers)
    if ret.status_code != 200:
        logger.error(f"publish app failed, {name} {ret.content}")
        return None
    else:
        logger.info(f"publish app success, {name}")
        return ret
