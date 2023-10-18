import os
from loguru import logger

import streamlit as st
import module.page as page
from templates.default import DefaultTemplate
from streamlit_extras.stylable_container import stylable_container

from module.utils import load_apps

logger.info("Loading release page")

page.page_header()

st.title("✈️ Release and share your app to friends")

app_col, template_col = st.columns([0.3, 0.7])
with app_col:
    with st.expander(":one: Select a app to release", expanded=True): 
        # select app
        # st.markdown("#### Select a app to release.")
        load_apps()
        apps = st.session_state['comfyflow_apps']
        app_opts = apps.keys()
        release_app = st.selectbox("My Apps", options=app_opts, key="release_app", help="Select a app to preview.")
        if 'release_app' in st.session_state.keys():
            logger.info(f"release app: {st.session_state['release_app']}")
        else:
            # check app status
            app_status = apps[release_app]['status']
            if app_status == 'created':
                st.warning(f"App {release_app} has not been previewed, please preview and check app first!")
            

    # release app
    with stylable_container(
            key="release_button",
            css_styles="""
                button {
                    background-color: rgb(28 131 225);
                    color: white;
                    border-radius: 4px;
                }
                button:hover, button:focus {
                    border: 0px solid rgb(28 131 225);
                }
            """,
        ):
        release_button = st.button("Release", help="Release your app with server-address", use_container_width=True)
        if release_button:
            port = os.getenv('COMFYFLOW_SERVER_PORT', default=8188)
            app_port = int(port) + int(apps[release_app]['id'])
            url = f"http://localhost:{app_port}"
            if apps[release_app]['status'] == 'previewed':
                # update app status
                from module.sqlitehelper import sqlitehelper
                if 'comfyflow_template' in st.session_state.keys():
                    template_name = st.session_state['comfyflow_template']
                sqlitehelper.update_app_release(release_app, url, template_name, "released")
            else:
                logger.info(f"App {release_app} has been released!")

            st.success(f"Release {release_app} success! You can share your app with url: {url}")


with template_col:
    with st.expander(":two: Select a template for app", expanded=True):
        # select template
        st.markdown("#### Release with default template.")
        api_data = apps[release_app]['api_conf']
        app_data = apps[release_app]['app_conf']
        server_addr = os.getenv('COMFYUI_SERVER_ADDR', default='localhost:8188')
        template_name = 'default'
        if template_name == 'default':
            comfy_flow = DefaultTemplate(server_addr=server_addr, api_data=api_data, app_data=app_data)
            if comfy_flow is not None:
                st.session_state['comfyflow_template'] = template_name
            

