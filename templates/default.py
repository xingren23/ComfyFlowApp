import json
from typing import Any

import streamlit as st
from modules.comfyflow import Comfyflow

class DefaultTemplate(Comfyflow):
    def __init__(self, comfy_client, api_data, app_data) -> Any:
    
        self.comfy_client = comfy_client
        self.api_json = json.loads(api_data)
        self.app_json = json.loads(app_data)

        self.create_ui(disabled=True)

    def generate(self):
        st.warning("Template not implemented yet!")
        

