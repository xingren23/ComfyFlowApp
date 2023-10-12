import requests
from loguru import logger
from module.comfyflow import Comfyflow

import streamlit as st
import streamlit_extras.app_logo as app_logo

NODE_CLASS_MAPPINGS = {}

def register_node_class(server_addr):
    object_info_url = f"http://{server_addr}/object_info"
    logger.info(f"Got object info from {object_info_url}")
    resp = requests.get(object_info_url, timeout=3)
    if resp.status_code != 200:
        raise Exception(f"Failed to get object info from {object_info_url}")
    object_info = resp.json()
    
    return object_info

st.set_page_config(page_title="ComfyFlowApp", layout="wide")

server_addr = st.session_state['server_addr']

app_logo.add_logo("public/images/logo.png", height=50)

# reduce top padding
st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)

# NODE_CLASS_MAPPINGS = register_node_class(server_addr)

workflow = st.selectbox("Workflows", options=["default", "sdxl_basic", "gen_mask"], index=0, key="workflow", help="Select a workflow")
api_file = f"conf/workflows/{workflow}/api.json"
app_file = f"conf/workflows/{workflow}/app.json"

comfy_flow = Comfyflow(server_addr=server_addr, api_file=api_file, app_file=app_file)