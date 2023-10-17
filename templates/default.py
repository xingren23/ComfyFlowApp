import json
from typing import Any
from PIL import Image
from loguru import logger

import streamlit as st
from module.comfyclient import ComfyClient

class DefaultTemplate:
    def __init__(self, server_addr, api_data, app_data, disabled=True) -> Any:
    
        self.comfy_client = ComfyClient(server_addr)
        self.api_json = json.loads(api_data)
        self.app_json = json.loads(app_data)

        self._create_ui(disabled=disabled)

    def generate(self):
        st.warning("Template not implemented yet!")
        
    def _create_ui_input(self, node_id, node_inputs):
        for param_item in node_inputs:
            param_type = node_inputs[param_item]['type']
            print(param_type)
            if param_type == "TEXT":
                param_name = node_inputs[param_item]['name']
                param_default = node_inputs[param_item]['default']
                param_help = node_inputs[param_item]['help']
                param_max = node_inputs[param_item]['max']
                            
                param_key = f"{node_id}_{param_name}"
                st.text_area(param_name, value =param_default, key=param_key, help=param_help, max_chars=param_max)
                if param_key not in st.session_state:   
                    st.session_state[param_key] = param_default
            elif param_type == "NUMBER":
                param_name = node_inputs[param_item]['name']
                param_default = node_inputs[param_item]['default']
                param_help = node_inputs[param_item]['help']
                param_min = node_inputs[param_item]['min']
                param_max = node_inputs[param_item]['max']
                param_step = node_inputs[param_item]['step']
                            
                param_key = f"{node_id}_{param_name}"
                st.number_input(param_name, value =param_default, key=param_key, help=param_help, min_value=param_min, max_value=param_max, step=param_step)
                if param_key not in st.session_state:
                    st.session_state[param_key] = param_default
            elif param_type == 'UPLOADIMAGE':
                param_name = node_inputs[param_item]['name']
                param_help = node_inputs[param_item]['help']
                param_subfolder = node_inputs[param_item].get('subfolder', '')
                param_key = f"{node_id}_{param_name}"
                uploaded_file = st.file_uploader(param_name, help=param_help, key=param_key, type=['png', 'jpg', 'jpeg'], accept_multiple_files=False)
                if uploaded_file is not None:
                    logger.info(f"uploading image, {uploaded_file}")
                    # upload to server
                    upload_type = "input"
                    imagefile = {'image': (uploaded_file.name, uploaded_file)}  # 替换为要上传的文件名和路径
                    self.comfy_client.upload_image(imagefile, param_subfolder, upload_type, 'true')

                    # show image preview
                    image = Image.open(uploaded_file)
                    st.image(image, use_column_width=True, caption='Input Image')

    def _create_ui(self, disabled):      
        logger.info("Creating UI")  

        st.title(f'{self.app_json["name"]}')
        st.markdown(f'{self.app_json["description"]}')
      
        st.divider()

        input_col, output_col = st.columns([0.4, 0.6], gap="medium")
        with input_col:
            # st.subheader('Inputs')
            with st.container():
                for node_id in self.app_json['inputs']:
                    node = self.app_json['inputs'][node_id]
                    node_inputs = node['inputs']
                    self._create_ui_input(node_id, node_inputs)

                submit = st.button(label='Generate', on_click=self.generate, disabled=disabled, use_container_width=True)

        with output_col:
            # st.subheader('Outputs')
            with st.container():
                if submit:
                    output_image = self.generate()
                    logger.info("update output_image")
                    st.image(output_image, use_column_width=True, caption='Output Image')
                else:
                    output_image = Image.open('./public/images/output-none.png')
                    logger.info("default output_image")
                    st.image(output_image, use_column_width=True, caption='None Image, Generate it!')

