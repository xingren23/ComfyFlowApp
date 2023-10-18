import os
from loguru import logger
from module.comfyflow import Comfyflow

import streamlit as st
import module.page as page
from module.utils import load_apps


logger.info("Loading preview page")

page.page_header()
st.title("💡 Preview and check app")

with st.container():
    load_apps()
    apps = st.session_state['comfyflow_apps']
    app_opts = apps.keys()
    preview_app = st.selectbox("My Apps", options=app_opts, key='preview_app', help="Select a app to preview.")
    if 'preview_app' in st.session_state.keys():
        logger.info(f"preview app: {st.session_state['preview_app']}")

    api_data = apps[preview_app]['api_conf']
    app_data = apps[preview_app]['app_conf']
    server_addr = os.getenv('COMFYUI_SERVER_ADDR', default='localhost:8188')
    comfy_flow = Comfyflow(server_addr=server_addr, api_data=api_data, app_data=app_data)
    if 'preview_result' in st.session_state.keys():
        preview_result = st.session_state['preview_result']
        # update app status
        if apps[preview_app]['status'] == 'created':
            from module.sqlitehelper import sqlitehelper
            sqlitehelper.update_app_preview(preview_result['name'], preview_result['image'])
            logger.info(f"Update app {preview_result['name']} status: previewed.")
        else:
            logger.info(f"App {preview_result['name']} has been previewed!")