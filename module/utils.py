import os
from loguru import logger
import streamlit as st

def listdirs(dir_path):
    # listdirs from local path
    if not os.path.exists(dir_path):
        return []
    return [d for d in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, d))]


def load_apps():
    from module.sqlitehelper import sqlitehelper
    apps = sqlitehelper.get_apps()
    app_map = {app['name']: app for app in apps}
    st.session_state['comfyflow_apps'] = app_map  
    logger.info(f"load apps: {app_map}")

def init_comfyui(server_addr):
    if 'comfy_object_info' not in st.session_state.keys():
        from module.comfyclient import ComfyClient
        try:
            server_addr = os.getenv('COMFYUI_SERVER_ADDR', default='localhost:8188')
            global comfy_client
            comfy_client = ComfyClient(server_addr=server_addr)
            comfy_object_info = comfy_client.get_node_class()
            st.session_state['comfy_object_info'] = comfy_object_info
            logger.info(f"init comfy object info: {comfy_object_info}")
        except Exception as e:
            st.error(f"Failed to get comfy object info, error: {e}")
            st.stop()

def format_node_info(param):
    # format {id}.{class_type}.{alias}.{param_name}
    node_id, class_type, class_name, param_name = param.split('.')
    return f"{class_name}:{param_name}"
