from loguru import logger

import streamlit as st
import modules.page as page
from templates.default import DefaultTemplate
from streamlit_extras.stylable_container import stylable_container

from modules.utils import load_apps, init_comfy_client

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
            if apps[release_app]['status'] == 'previewed':
                # update app status
                from modules.sqlitehelper import sqlitehelper
                if 'comfyflow_template' in st.session_state.keys():
                    template_name = st.session_state['comfyflow_template']
                sqlitehelper.update_app_release(release_app, template_name, "released")
            else:
                logger.info(f"App {release_app} has been released!")

            st.success(f"Release {release_app} success")


with template_col:
    with st.expander(":two: Select a template for app", expanded=True):
        # select template
        st.markdown("#### Release with default template.")
        api_data = apps[release_app]['api_conf']
        app_data = apps[release_app]['app_conf']

        comfy_client = init_comfy_client()
        comfy_client = st.session_state['comfy_client']

        template_name = 'default'
        if template_name == 'default':
            comfy_flow = DefaultTemplate(comfy_client=comfy_client, api_data=api_data, app_data=app_data)
            if comfy_flow is not None:
                st.session_state['comfyflow_template'] = template_name
            

