import streamlit as st
import argparse
from loguru import logger
from streamlit_extras.badges import badge

from modules import get_sqlite_instance, get_comfy_client

def page_header():    
    st.set_page_config(page_title="ComfyFlowApp: Load a comfyui workflow as webapp in seconds.", 
    page_icon=":artist:", layout="wide")

    # reduce top padding
    st.markdown("""
            <style>
                .block-container {
                        padding-top: 1rem;
                        padding-bottom: 0rem;
                        # padding-left: 5rem;
                        # padding-right: 5rem;
                    }
            </style>
            """, unsafe_allow_html=True)
    
    hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

    with st.sidebar:    
        st.sidebar.markdown("""
        <style>
        [data-testid='stSidebarNav'] > ul {
            min-height: 70vh;
        } 
        </style>
        """, unsafe_allow_html=True)

        st.image("public/images/logo.png", width=200)

        st.sidebar.markdown("""
                            ### ComfyFlowApp
                            Load a comfyui workflow as webapp in seconds.
                            """)

        badge(type="github", name="xingren23/ComfyFlowApp", url="https://github.com/xingren23/ComfyFlowApp")
        badge(type="twitter", name="xingren23", url="https://twitter.com/xingren23")

parser = argparse.ArgumentParser(description='Comfyflow manager')
parser.add_argument('--app', type=str, default='', help='comfyflow app id')
args = parser.parse_args()

page_header()

with st.container():
    apps = get_sqlite_instance().get_all_apps()
    app_id_map = { str(app.id): app for app in apps} 
    app_id = args.app
    logger.info(f"load app app_id {app_id}")

    if app_id not in app_id_map:
        st.warning(f"App {app_id} hasn't existed")
    else:
        app = app_id_map[app_id]
        app_data = app.app_conf
        api_data = app.api_conf

        from modules.comfyflow import Comfyflow
        comfy_flow = Comfyflow(comfy_client=get_comfy_client(), api_data=api_data, app_data=app_data)
        comfy_flow.create_ui(show_header=True)