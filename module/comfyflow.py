import json
from typing import Any
import random
from PIL import Image
from loguru import logger

import streamlit as st
from module.comfyclient import ComfyClient

class Comfyflow:
    def __init__(self, server_addr, api_file, app_file) -> Any:
    
        self.comfy_client = ComfyClient(server_addr)
        with open(api_file) as f:
            logger.info(f"Loading api data from {api_file}")
            self.api_data = json.load(f)
        with open(app_file) as f:
            logger.info(f"Loading app data from {app_file}")
            self.app_data = json.load(f)
        
        assert self.api_data is not None
        assert self.app_data is not None

        self.app = self._create_ui()

        pass

    def generate(self):
        prompt = self.api_data
        #set prompt inputs
        for node_id in self.app_data['inputs']:
            node = self.app_data['inputs'][node_id]
            node_inputs = node['inputs']
            for param_item in node_inputs:
                param_type = node_inputs[param_item]['type']
                if param_type == "STRING":
                    param_name = node_inputs[param_item]['name']
                    param_key = f"{node_id}_{param_name}"
                    param_value = st.session_state[param_key]
                    logger.info(f"update param {param_name} {param_value}")
                    prompt[node_id]["inputs"][param_item] = param_value
                elif param_type == "INT":
                    param_name = node_inputs[param_item]['name']
                    param_key = f"{node_id}_{param_name}"
                    param_value = st.session_state[param_key]
                    logger.info(f"update param {param_name} {param_value}")
                    if (param_name == "seed" or param_name == "noise_seed") and param_value == -1:
                        param_max = node_inputs[param_item]['max']
                        param_value = random.randint(0, param_max)
                        logger.info(f"update random param {param_name} {param_value}")
                        st.session_state[param_key] = param_value
                    
                    prompt[node_id]["inputs"][param_item] = param_value
                elif param_type == 'IMAGE':
                    param_name = node_inputs[param_item]['name']
                    param_key = f"{node_id}_{param_name}"
                    if param_key in st.session_state:
                        param_value = st.session_state[param_key]
                        
                        logger.info(f"update param {param_name} {param_value}")
                        if param_value is not None:
                            prompt[node_id]["inputs"][param_item] = param_value.name
                        else:
                            st.error(f"Please select input image for {param_name}")

        #set prompt outputs
        logger.info(f"Sending prompt to server, {prompt}")
        images = self.comfy_client.gen_images(prompt)
        for node_id in self.app_data['outputs']:
            image_data = images[node_id]
            break
        return image_data
        

    def _create_ui_input(self, node_id, node_inputs):
        for param_item in node_inputs:
            param_type = node_inputs[param_item]['type']
            print(param_type)
            if param_type == "STRING":
                param_name = node_inputs[param_item]['name']
                param_default = node_inputs[param_item]['default']
                param_help = node_inputs[param_item]['help']
                param_max = node_inputs[param_item]['max']
                            
                param_key = f"{node_id}_{param_name}"
                st.text_area(param_name, value =param_default, key=param_key, help=param_help, max_chars=param_max)
                if param_key not in st.session_state:   
                    st.session_state[param_key] = param_default
            elif param_type == "INT":
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
            elif param_type == 'IMAGE':
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

    def _create_ui(self):      
        logger.info("Creating UI")  

        st.title(f'{self.app_data["description"]}')

        # header_col, logo_col, git_col = st.columns([0.82, 0.15, 0.03], gap="small")
        # with header_col:
        #     st.title(f'✈️ {self.app_data["description"]}')
        # with logo_col:
        #     st.markdown("")
        #     st.link_button(':point_right: Star ComfyFlowApp', url='https://github.com/xingren23/ComfyFlowApp')
        # with git_col:
        #     st.markdown("")
        #     st.markdown("[![Github](https://img.icons8.com/material-outlined/32/000000/github.png)](https://github.com/xingren23/ComfyFlowApp)")
            
        st.divider()

        input_col, output_col = st.columns([0.4, 0.6], gap="medium")
        with input_col:
            # st.subheader('Inputs')
            with st.container():
                for node_id in self.app_data['inputs']:
                    node = self.app_data['inputs'][node_id]
                    node_inputs = node['inputs']
                    self._create_ui_input(node_id, node_inputs)

                submit = st.button(label='Generate', on_click=self.generate, use_container_width=True)

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


