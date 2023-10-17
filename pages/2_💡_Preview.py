import os
from loguru import logger
from module.comfyflow import Comfyflow

import streamlit as st
import module.header as header
import module.utils as utils


logger.info("Loading workflow page")

header.page_header()
st.title("💡 Preview and check app")

with st.container():
    apps = utils.get_apps()
    # app_map: {app_name: app_data}
    app_map = {app['name']: app for app in apps}
    app_opts = [app['name'] for app in apps]
    preview_app = st.selectbox("My Apps", options=app_opts, key='preview_app', help="Select a app to preview.")
    if 'preview_app' in st.session_state.keys():
        logger.info(f"preview app: {st.session_state['preview_app']}")

    api_data = app_map[preview_app]['api_conf']
    app_data = app_map[preview_app]['app_conf']


server_addr = os.getenv('COMFYUI_SERVER_ADDR', default='localhost:8188')
comfy_flow = Comfyflow(server_addr=server_addr, api_data=api_data, app_data=app_data)