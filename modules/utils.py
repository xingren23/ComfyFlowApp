import os
from loguru import logger
import streamlit as st

def listdirs(dir_path):
    # listdirs from local path
    if not os.path.exists(dir_path):
        return []
    return [d for d in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, d))]


def load_apps():
    from modules.sqlitehelper import sqlitehelper
    apps = sqlitehelper.get_apps()
    app_map = {app['name']: app for app in apps}
    st.session_state['comfyflow_apps'] = app_map  
    app_id_map = {app['id']: app for app in apps}
    st.session_state['comfyflow_apps_id'] = app_id_map
    logger.info(f"load apps: {app_map.keys()}")

def init_comfy_client():
    if 'comfy_client' not in st.session_state.keys():
        from modules.comfyclient import ComfyClient
        try:
            server_addr = os.getenv('COMFYUI_SERVER_ADDR', default='localhost:8188')
            comfy_client = ComfyClient(server_addr=server_addr)
            st.session_state['comfy_client'] = comfy_client
            
            logger.info(f"init comfy_client: {server_addr}")
        except Exception as e:
            st.error(f"Failed to get comfy object info, error: {e}")
            st.stop()

def init_comfy_object_info():
    if 'comfy_object_info' not in st.session_state.keys():
        try:
            init_comfy_client()
            comfy_client = st.session_state['comfy_client']
            comfy_object_info = comfy_client.get_node_class()
            st.session_state['comfy_object_info'] = comfy_object_info
            logger.debug(f"init comfy object info: {comfy_object_info.keys()}")
        except Exception as e:
            st.error(f"Failed to get comfy object info, error: {e}")
            st.stop()            
