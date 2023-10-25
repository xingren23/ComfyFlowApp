from loguru import logger
from modules.comfyflow import Comfyflow

import streamlit as st
import modules.page as page
from modules import get_comfy_client, get_sqlite_instance


logger.info("Loading preview page")
page.page_init()

with st.container():
    st.title("💡 Preview and check app")

    apps = get_sqlite_instance().get_all_apps()
    app_name_map = {app['name']: app for app in apps}
    app_opts = list(app_name_map.keys())
    if len(app_opts) == 0:
        st.warning("Please create a new app first.")
        st.stop()
    else:
        st.selectbox("My Apps", options=app_opts, key='preview_select_app', help="Select a app to preview.")
        
        preview_app = st.session_state['preview_select_app']
        if preview_app:
            logger.info(f"preview app: {preview_app}")
            
            app = app_name_map[preview_app]
            api_data = app['api_conf']
            app_data = app['app_conf']
            comfyflow = Comfyflow(comfy_client=get_comfy_client(), api_data=api_data, app_data=app_data)
            comfyflow.create_ui()