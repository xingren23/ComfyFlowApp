import os
import streamlit as st
import argparse

from modules.utils import load_apps
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
        # badge(type="buymeacoffee", name="comfyflow", url="https://www.buymeacoffee.com/comfyflow")
        st.markdown("""
                [!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/comfyflow)
                """)

parser = argparse.ArgumentParser(description='Comfyflow manager')
parser.add_argument('--app', type=str, default='', help='comfyflow app name')
args = parser.parse_args()


page_header()

with st.container():
    load_apps()
    app_name = args.app
    apps = st.session_state['comfyflow_apps']

    if app_name not in apps.keys():
        st.warning(f"App {app_name} does not exist!")
    else:
        app_status = apps[app_name]['status']
        if app_status == 'released':
            app_data = apps[app_name]['app_conf']
            api_data = apps[app_name]['api_conf']
            server_addr = os.getenv('COMFYUI_SERVER_ADDR', default='localhost:8188')
            from modules.comfyflow import Comfyflow
            comfy_flow = Comfyflow(server_addr=server_addr, api_data=api_data, app_data=app_data)
        else:
            st.warning(f"App hasn't released, {app_name} status {app_status}")