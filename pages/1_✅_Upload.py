
import os
from datetime import datetime
from loguru import logger
from PIL import Image, ImageOps
from PIL.PngImagePlugin import PngInfo
import json

import streamlit as st
import module.header as header
from module.comfyclient import ComfyClient
from module import default_server_addr


logger.info("Loading upload page")

def process_workflow_meta(image_upload, savefile):
    # parse meta data from image, save image to local
    try:
        logger.info(f"process_workflow_meta, {image_upload}")
        img = Image.open(image_upload)
        tran_img = ImageOps.exif_transpose(img)

        # save meta data to file
        if savefile:
            # get filename and extension
            file_id = image_upload.file_id
            file_name, _ = os.path.splitext(os.path.basename(image_upload.name))
            save_to_file = f'uploads/{datetime.today().strftime("%Y-%m-%d")}/{file_id}_{file_name}.png'
            
            os.makedirs(os.path.dirname(save_to_file), exist_ok=True)
            metadata = PngInfo()
            for x in tran_img.info:
                logger.info(f"image meta data, {x}:{tran_img.info[x]}")
                # save as json file
                file_path = f'uploads/{datetime.today().strftime("%Y-%m-%d")}/{file_id}_{file_name}_{x}.json'
                with open(file_path, 'w') as json_file:
                    json_file.write(tran_img.info[x])

                #TODO: fix no metadata 
                metadata.add_text(x, json.dumps(img.info[x]))
            logger.info(f"save image to {save_to_file} with meta data, {metadata}")
            img.save(save_to_file, format='png', PngInfo=metadata, compress_level=4)

        return tran_img.info    
    except Exception as e:
        logger.error(f"process_workflow_meta error, {e}")
        return None
    

def parse_prompt(prompt_info):
    # parse prompt to inputs and outputs
    try:
        prompt = json.loads(prompt_info)
        params_inputs = []
        params_outputs = []
        logger.info(f"parse_prompt, {prompt}")
        for node_id in prompt:
            node = prompt[node_id]
            class_type = prompt[node_id]['class_type']
            for param in node['inputs']:
                param_value = node['inputs'][param]
                param_key = f"{node_id}.{class_type}.{param}"
                logger.info(f"parse_prompt, {param_key} {param_value}")
                # check param_value is []
                if isinstance(param_value, list):
                    logger.info(f"ignore {param_key}, param_value is list, {param_value}")
                    continue
                if param == "choose file to upload":
                    logger.info(f"ignore {param_key}, param for 'choose file to upload'")
                    continue

                is_output = st.session_state['comfy_object_info'][class_type]['output_node']
                if is_output:
                    params_outputs.append(param_key)
                else:
                    params_inputs.append(param_key)

        return params_inputs, params_outputs
    except Exception as e:
        logger.error(f"parse_prompt error, {e}")
        return None, None

def process_image_change():
    logger.info(f"process_image_change session , {st.session_state['upload_image']}")
    if not st.session_state['upload_image']:
        logger.info("clear upload_prompt_inputs and upload_prompt_outputs")
        st.session_state['upload_prompt'] = None
        st.session_state['upload_prompt_inputs'] = []
        st.session_state['upload_prompt_outputs'] = []


def get_node_input_config(input_param):
    node_id, class_type, param = input_param.split('.')
    class_meta = st.session_state['comfy_object_info'][class_type]
    class_input = class_meta['input']['required']
    if 'optional' in class_meta['input'].keys():
        class_input.update(class_meta['input']['optional'])
    
    logger.info(f"{node_id} {class_type} {param}, class input {class_input}")

    input_config = {}
    if isinstance(class_input[param][0], str):
        
        if class_input[param][0] == 'STRING':
            input_config = {
                "inputs": {
                    param: {
                        "type": "TEXT",
                        "name": input_param,
                        "help": "Input a string",
                        "default": "",
                        "max": 300,
                    }
                }
            }
        elif class_input[param][0] == 'INT':
            defaults = class_input[param][1]
            input_config = {
                "inputs": {
                    param: {
                        "type": "NUMBER",
                        "name": input_param,
                        "help": "Input a int",
                        "default": defaults.get('default', 0),
                        "min": defaults.get('min', 0),
                        "max": min(defaults.get('max', 100), 4503599627370496),
                        "step": defaults.get('step', 1),
                    }
                }
            }
        elif class_input[param][0] == 'FLOAT':
            defaults = class_input[param][1]
            input_config = {
                "inputs": {
                    param: {
                        "type": "NUMBER",
                        "name": input_param,
                        "help": "Input a float",
                        "default": defaults.get('default', 0),
                        "min": defaults.get('min', 0),
                        "max": min(defaults.get('max', 100), 4503599627370496),
                        "step": defaults.get('step', 1),
                    }
                }
            }
    elif isinstance(class_input[param][0], list):
        if class_type == 'LoadImage' and param == 'image':
            input_config = {
                "inputs": {
                    param: {
                        "type": "UPLOADIMAGE",
                        "name": input_param,
                        "help": "UpLoad image from local file",
                    }
                }
            }
        else:
            input_config = {
                "inputs": {
                    param: {
                        "type": "SELECT",
                        "name": input_param,
                        "help": "Select a option",
                        "options": class_input[param][0],
                    }
                }
            }
    return node_id, input_config

def get_node_output_config(output_param):
    node_id, class_type, param = output_param.split('.')
    output_param_inputs =  {
        "outputs": {
        }
    }
    return node_id, output_param_inputs

def step1_upload_image():
    with st.expander("### :one: Upload image of comfyui workflow", expanded=True):
        image_col1, image_col2 = st.columns([0.5, 0.5])
        with image_col1:
            image_upload = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"], key="upload_image", on_change=process_image_change, help="upload image of comfyui workflow")
        with image_col2:   
            if image_upload:
                metas = process_workflow_meta(image_upload, True)
                if metas and 'prompt' in metas.keys() and 'workflow' in metas.keys():
                    st.session_state['upload_prompt'] = metas.get('prompt')
                    inputs, outputs = parse_prompt(metas.get('prompt'))
                    if inputs and outputs:
                        logger.info(f"upload_prompt_inputs, {inputs}")
                        st.session_state['upload_prompt_inputs'] = inputs
                        logger.info(f"upload_prompt_outputs, {outputs}")
                        st.session_state['upload_prompt_outputs'] = outputs

                        image_col1, image_col, col3 = st.columns([0.2, 0.6, 0.2])
                        with image_col:
                            st.image(image_upload, use_column_width=True, caption='ComfyUI Workflow Image, include workflow meta data')
                else:
                    st.error(f"this image don't generated by a comfyui workflow, please upload again")

def step2_config_params():
    with st.expander("### :two: Config params of workflow app"):
        with st.container():
            name_col1, desc_col2 = st.columns([0.2, 0.8])
            with name_col1:
                st.text_input("App Name", value="", placeholder="input app name", key="app_name", help="Input app name")
            with desc_col2:
                st.text_input("App Description", value="", placeholder="input app description", key="app_desc", help="Input app description")

        param_col1, param_col2 = st.columns([0.5, 0.5])
        with param_col1:
            params_inputs = st.session_state.get('upload_prompt_inputs', [])
            st.selectbox("Input Param", options=params_inputs, key="input_param1", help="Select a param from workflow")
            st.selectbox("Input Param", options=params_inputs, key="input_param2", help="Select a param from workflow")
        with param_col2:
            params_outputs = st.session_state.get('upload_prompt_outputs', [])
            st.selectbox("Output Param", options=params_outputs, key="output_param1", help="Select a param from workflow")
  

header.page_header()

with st.container():
    if 'comfy_object_info' not in st.session_state.keys():
        server_addr = st.session_state.get('server_addr', default=default_server_addr)
        comfy_client = ComfyClient(server_addr=server_addr)
        comfy_object_info = comfy_client.get_node_class()
        st.session_state['comfy_object_info'] = comfy_object_info

    st.title(":100: Upload a comfyui workflow, run it as webapp")

    # upload workflow image and config params
    step1_upload_image()
    step2_config_params()
    
    with st.container():
        # button style
        # st.markdown(
        #     """
        #     <style>
        #     button {
        #         height: auto;
        #             padding-top: 10px !important;
        #             padding-bottom: 10px !important;
        #         }
        #     </style>
        #     """,
        #     unsafe_allow_html=True,
        # )
        submit_button = st.button("Submit", type="primary", key='submit_workflow', use_container_width=True,help="Submit workflow app")
        if submit_button:
            # check app dir
            workflow_path = f'workflows/{st.session_state["app_name"]}'
            os.makedirs(workflow_path, exist_ok=True)

            prompt = st.session_state['upload_prompt']
            input_param1 = st.session_state['input_param1']
            output_param1 = st.session_state['output_param1']
            app_name = st.session_state['app_name']
            app_desc = st.session_state['app_desc']
            if prompt and input_param1 and output_param1 and app_name and app_desc:
                # gen and upload app.json 
                app_config = {
                    "name": app_name,
                    "description": app_desc,
                    "inputs": {},
                    "outputs": {}
                }
                # parse input_param1
                node_id, input_param1_inputs = get_node_input_config(input_param1)
                app_config['inputs'][node_id] = input_param1_inputs 
                input_param2 = st.session_state['input_param2']
                if input_param2:
                    node_id, input_param2_inputs = get_node_input_config(input_param2)
                    app_config['inputs'][node_id] = input_param2_inputs

                # parse output_param1
                node_id, output_param1_inputs = get_node_output_config(output_param1)
                app_config['outputs'][node_id] = output_param1_inputs

                # save app config
                app_file_path = f'{workflow_path}/app.json'
                with open(app_file_path, 'w') as f:
                    # dump dict to file
                    logger.info(f"save app config to {app_file_path}, {app_config}")
                    json.dump(app_config, f)

                # upload prompt.json
                prompt_file_path = f'{workflow_path}/prompt.json'
                with open(prompt_file_path, 'w') as f:
                    # write string to file
                    logger.info(f"save prompt to {prompt_file_path}, {prompt}")
                    f.write(st.session_state['upload_prompt'])

                st.success("Submit workflow app successfully")
            else:
                st.error("Submit workflow app failed, please check workflow image and config params")
