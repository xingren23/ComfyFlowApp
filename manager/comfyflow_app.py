import streamlit as st
import argparse

from modules.utils import load_apps, init_comfy_client
from streamlit_extras.badges import badge

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
    load_apps()
    apps = st.session_state['comfyflow_apps_id']
    
    app_id = int(args.app)
    if app_id not in apps.keys():
        st.warning(f"App {app_id} does not exist in apps: {apps.keys()}")
    else:
        app_status = apps[app_id]['status']
        if app_status == 'released':
            app_data = apps[app_id]['app_conf']
            api_data = apps[app_id]['api_conf']

            init_comfy_client()
            comfy_client = st.session_state['comfy_client']

            from modules.comfyflow import Comfyflow
            comfy_flow = Comfyflow(comfy_client=comfy_client, api_data=api_data, app_data=app_data)
        else:
            st.warning(f"App hasn't released, {app_id} status {app_status}")