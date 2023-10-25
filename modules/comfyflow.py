from typing import Any
import random
import json
import copy
from PIL import Image
from loguru import logger
import queue

import streamlit as st
from modules.page import custom_text_area

class Comfyflow:
    def __init__(self, comfy_client, api_data, app_data) -> Any:
    
        self.comfy_client = comfy_client
        self.api_json = json.loads(api_data)
        self.app_json = json.loads(app_data)

    def generate(self):
        prompt = copy.deepcopy(self.api_json)
        if prompt is not None:
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
                            
            logger.info(f"Sending prompt to server, {prompt}")
            queue = st.session_state.get('progress_queue', None)
            prompt_id = self.comfy_client.gen_images(prompt, queue)
            st.session_state['preview_prompt_id'] = prompt_id

    def get_output_images(self):
        # get output images by prompt_id
        prompt_id = st.session_state['preview_prompt_id']
        if prompt_id is None:
            return None
        history = self.comfy_client.get_history(prompt_id)[prompt_id]
        for node_id in self.app_json['outputs']:
            node_output = history['outputs'][node_id]
            if 'images' in node_output:
                images_output = []
                for image in node_output['images']:
                    image_data = self.comfy_client.get_image(image['filename'], image['subfolder'], image['type'])
                    images_output.append(image_data)
                    
                logger.info(f"Got images from server, {node_id}, {len(images_output)}")
                return images_output
        

    def create_ui_input(self, node_id, node_inputs):
        custom_text_area()
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
                st.text_area(param_name, value =param_default, key=param_key, help=param_help, max_chars=param_max, height=500)
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

        if 'progress_queue' not in st.session_state:   
            st.session_state['progress_queue'] = queue.Queue()
        
        app_name = self.app_json['name']
        app_description = self.app_json['description']
        st.title(f'{app_name}')
        st.markdown(f'{app_description}')
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

                gen_button = st.button(label='Generate', use_container_width=True, disabled=disabled, on_click=self.generate)


        with output_col:
            # st.subheader('Outputs')
            with st.container():
                node_size = len(self.api_json)
                executed_nodes = []
                queue_remaining = self.comfy_client.queue_remaining()
                output_queue_remaining = st.text(f"Queue: {queue_remaining}")
                progress_placeholder = st.empty()
                img_placeholder = st.empty()
                if gen_button:
                    # update progress
                    output_progress = progress_placeholder.progress(value=0.0, text="Generate image")
                    while True:
                        try:
                            progress_queue = st.session_state.get('progress_queue')
                            event = progress_queue.get()
                            logger.debug(f"event: {event}")

                            event_type = event['type']
                            if event_type == 'status':
                                remaining = event['data']['exec_info']['queue_remaining']
                                output_queue_remaining.text(f"Queue: {remaining}")
                            elif event_type == 'execution_cached':
                                executed_nodes.extend(event['data']['nodes'])
                                output_progress.progress(len(executed_nodes)/node_size, text="Generate image...")
                            elif event_type == 'executing':
                                node = event['data']
                                if node is None:
                                    output_image = self.get_output_images()
                                    if output_image is not None:
                                        img_placeholder.image(output_image, use_column_width=True, caption='Output Image')

                                    output_progress.progress(len(executed_nodes)/node_size, text="Generate image finished")
                                    logger.info("Generating image finished")
                                    st.session_state[f'{app_name}_previewed'] = True
                                    break
                                else:
                                    executed_nodes.append(node)
                                    output_progress.progress(len(executed_nodes)/node_size, text="Generating image...")
                            elif event_type == 'b_preview':
                                preview_image = event['data']
                                img_placeholder.image(preview_image, use_column_width=True, caption="Preview")
                        except Exception as e:
                            logger.warning(f"get progress exception, {e}")
                            st.warning(f"get progress exception {e}")
                else:
                    output_image = Image.open('./public/images/output-none.png')
                    logger.info("default output_image")
                    img_placeholder.image(output_image, use_column_width=True, caption='None Image, Generate it!')

                
    

