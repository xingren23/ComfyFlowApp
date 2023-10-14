import os
from loguru import logger
from module.comfyflow import Comfyflow

import streamlit as st
import module.header as header

from module import default_server_addr

logger.info("Loading workflow page")

header.page_header()

def listdirs(dir_path):
    # listdirs from local path
    dirs = [d for d in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, d))]
    return dirs

if 'workflow_opts' not in st.session_state.keys():
    workflows = listdirs('workflows')
    logger.info(f"list workflows, {workflows}")
    st.session_state['workflow_opts'] = workflows

workflow_opts = st.session_state.get('workflow_opts', default=[])
workflow = st.selectbox("Workflows", options=workflow_opts, key="select_workflow", help="Select a workflow")


api_file = f"workflows/{workflow}/prompt.json"
app_file = f"workflows/{workflow}/app.json"

server_addr = st.session_state.get('server_addr', default=default_server_addr)
comfy_flow = Comfyflow(server_addr=server_addr, api_file=api_file, app_file=app_file)