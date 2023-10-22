from loguru import logger
from modules.comfyflow import Comfyflow

import streamlit as st
import modules.page as page
from modules.utils import load_apps, init_comfy_client

logger.info("Loading preview page")

page.page_header()
st.title("💡 Preview and check app")

with st.container():
    load_apps()
    apps = st.session_state['comfyflow_apps']
    app_opts = apps.keys()
    preview_app = st.selectbox("My Apps", options=app_opts, key='preview_app', help="Select a app to preview.")
    if preview_app is not None:
        logger.info(f"preview app: {st.session_state['preview_app']}")

        api_data = apps[preview_app]['api_conf']
        app_data = apps[preview_app]['app_conf']
        
        init_comfy_client()
        comfy_client = st.session_state['comfy_client']

        comfy_flow = Comfyflow(comfy_client=comfy_client, api_data=api_data, app_data=app_data)
        if 'preview_result' in st.session_state.keys():
            preview_result = st.session_state['preview_result']
            # update app status
            if apps[preview_app]['status'] == 'created':
                from modules.sqlitehelper import sqlitehelper
                sqlitehelper.update_app_preview(preview_result['name'], preview_result['image'])
                logger.info(f"Update app {preview_result['name']} status: previewed.")
            else:
                logger.info(f"App {preview_result['name']} has been previewed!")
    else:
        st.warning("Please create a new app first.")