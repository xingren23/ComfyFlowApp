from typing import Any
import random
import json
import copy
from PIL import Image
from loguru import logger

import streamlit as st
from modules.comfyclient import ComfyClient

class Comfyflow:
    def __init__(self, server_addr, api_data, app_data) -> Any:
    
        self.comfy_client = ComfyClient(server_addr)
        self.api_json = json.loads(api_data)
        self.app_json = json.loads(app_data)
        self.create_ui()

    def generate(self):
        prompt = copy.deepcopy(self.api_json)
        #set prompt inputs
        for node_id in self.app_json['inputs']:
            node = self.app_json['inputs'][node_id]
            node_inputs = node['inputs']
            for param_item in node_inputs:
                logger.info(f"update param {param_item}, {node_inputs[param_item]}")
                param_type = node_inputs[param_item]['type']
                if param_type == "TEXT":
                    param_name = node_inputs[param_item]['name']
                    param_key = f"{node_id}_{param_name}"
                    param_value = st.session_state[param_key]
                    logger.info(f"update param {param_key} {param_name} {param_value}")
                    prompt[node_id]["inputs"][param_item] = param_value

                elif param_type == "NUMBER":
                    param_name = node_inputs[param_item]['name']
                    param_key = f"{node_id}_{param_name}"
                    param_value = st.session_state[param_key]
                    logger.info(f"update param {param_key} {param_name} {param_value}")
                    if (param_name == "seed" or param_name == "noise_seed") and param_value == -1:
                        param_max = node_inputs[param_item]['max']
                        param_value = random.randint(0, param_max)
                        logger.info(f"update random param {param_name} {param_value}")
                        st.session_state[param_key] = param_value
                    
                    prompt[node_id]["inputs"][param_item] = param_value

                elif param_type == "SELECT":
                    param_name = node_inputs[param_item]['name']
                    param_key = f"{node_id}_{param_name}"
                    param_value = st.session_state[param_key]
                    logger.info(f"update param {param_key} {param_name} {param_value}")
                    prompt[node_id]["inputs"][param_item] = param_value

                elif param_type == "CHECKBOX":
                    param_name = node_inputs[param_item]['name']
                    param_key = f"{node_id}_{param_name}"
                    param_value = st.session_state[param_key]
                    logger.info(f"update param {param_key} {param_name} {param_value}")
                    prompt[node_id]["inputs"][param_item] = param_value

                elif param_type == 'UPLOADIMAGE':
                    param_name = node_inputs[param_item]['name']
                    param_key = f"{node_id}_{param_name}"
                    if param_key in st.session_state:
                        param_value = st.session_state[param_key]
                        
                        logger.info(f"update param {param_key} {param_name} {param_value}")
                        if param_value is not None:
                            prompt[node_id]["inputs"][param_item] = param_value.name
                        else:
                            st.error(f"Please select input image for param {param_name}")
                            return
                            

        #set prompt outputs
        if prompt is not None:
            logger.info(f"Sending prompt to server, {prompt}")
            images = self.comfy_client.gen_images(prompt)
            for node_id in self.app_json['outputs']:
                image_data = images[node_id]
            return image_data
        

    def create_ui_input(self, node_id, node_inputs):
        for param_item in node_inputs:
            param_node = node_inputs[param_item]
            logger.info(f"create ui input: {param_item} {param_node}")
            param_type = param_node['type']
            if param_type == "TEXT":
                param_name = param_node['name']
                param_default = param_node['default']
                param_help = param_node['help']
                param_max = param_node['max']
                            
                param_key = f"{node_id}_{param_name}"
                st.text_area(param_name, value =param_default, key=param_key, help=param_help, max_chars=param_max)
            elif param_type == "NUMBER":
                param_name = param_node['name']
                param_default = param_node['default']
                param_help = param_node['help']
                param_min = param_node['min']
                param_max = param_node['max']
                param_step = param_node['step']
                            
                param_key = f"{node_id}_{param_name}"
                st.number_input(param_name, value =param_default, key=param_key, help=param_help, min_value=param_min, max_value=param_max, step=param_step)
            elif param_type == "SELECT":
                param_name = param_node['name']
                param_default = param_node['default']
                param_help = param_node['help']
                param_options = param_node['options']

                param_key = f"{node_id}_{param_name}"
                st.selectbox(param_name, options=param_options, key=param_key, help=param_help)

            elif param_type == "CHECKBOX":
                param_name = param_node['name']
                param_default = param_node['default']
                param_help = param_node['help']

                param_key = f"{node_id}_{param_name}"
                st.checkbox(param_name, value=param_default, key=param_key, help=param_help)
            elif param_type == 'UPLOADIMAGE':
                param_name = param_node['name']
                param_help = param_node['help']
                param_subfolder = param_node.get('subfolder', '')
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

    def create_ui(self, disabled=False):      
        logger.info("Creating UI")  

        st.title(f'{self.app_json["name"]}')
        st.markdown(f'{self.app_json["description"]}')
        st.divider()

        input_col, output_col = st.columns([0.4, 0.6], gap="medium")
        with input_col:
            # st.subheader('Inputs')
            with st.container():
                logger.info(f"app_data: {self.app_json}")
                for node_id in self.app_json['inputs']:
                    node = self.app_json['inputs'][node_id]
                    node_inputs = node['inputs']
                    self.create_ui_input(node_id, node_inputs)

                submit = st.button(label='Generate', use_container_width=True, disabled=disabled)

        with output_col:
            # st.subheader('Outputs')
            with st.container():
                if submit:
                    output_image = self.generate()
                    if output_image is None:
                        st.error('Generate Failed!')
                    else:
                        logger.info("update output_image")
                        st.image(output_image, use_column_width=True, caption='Output Image')

                        # update preview image with first output image
                        preview_image = output_image[0]
                        st.session_state['preview_result'] = {'name': self.app_json['name'], 'image': preview_image}

                        st.success('Generate Success!')
                else:
                    output_image = Image.open('./public/images/output-none.png')
                    logger.info("default output_image")
                    st.image(output_image, use_column_width=True, caption='None Image, Generate it!')

