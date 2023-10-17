import os
from loguru import logger

import streamlit as st
import module.header as header
from templates.default import DefaultTemplate
from streamlit_extras.stylable_container import stylable_container

import module.utils as utils


logger.info("Loading release page")

def listdirs(dir_path):
    # listdirs from local path
    dirs = [d for d in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, d))]
    return dirs

header.page_header()

st.title("✈️ Release and share your app to friends")

# select app
apps = utils.get_apps()
app_map = {app['name']: app for app in apps}

with st.expander(":one: Select a app to release", expanded=True): 
    app_opts = [app['name'] for app in apps]
    release_app = st.selectbox("My Apps", options=app_opts, key="release_app", help="Select a app to preview.")
    if 'release_app' in st.session_state.keys():
        logger.info(f"release app: {st.session_state['release_app']}")

with st.expander(":two: Select a template for app", expanded=True):
    # select template
    st.markdown("#### Preview with default template.")
    
    api_data = app_map[release_app]['api_conf']
    app_data = app_map[release_app]['app_conf']
    server_addr = os.getenv('COMFYUI_SERVER_ADDR', default='localhost:8188')
    col1, col_main, col3 = st.columns([0.1, 0.8, 0.1])
    with col_main:
        comfy_flow = DefaultTemplate(server_addr=server_addr, api_data=api_data, app_data=app_data, disabled=True)

# release app
with stylable_container(
        key="new_app_button",
        css_styles="""
            button {
                background-color: rgb(28 131 225);
                color: white;
                border-radius: 4px;
            }
            button:hover {
                border: 0px solid rgb(28 131 225);
            }
        """,
    ):
    release_button = st.button("Release", help="Release your app with server-address", use_container_width=True)