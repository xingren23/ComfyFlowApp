import os
from datetime import datetime
from loguru import logger
from PIL import Image, ImageOps
from PIL.PngImagePlugin import PngInfo
import json

import streamlit as st
import modules.page as page
from streamlit_extras.row import row
from streamlit_extras.stylable_container import stylable_container
from modules.utils import init_comfyui

server_addr = os.getenv('COMFYUI_SERVER_ADDR', default='localhost:8188')
logger.info(f"Loading create page, server_addr: {server_addr}")

page.page_header()

init_comfyui(server_addr)

NODE_SEP = '||'


def format_input_node_info(param):
    # format {id}.{class_type}.{alias}.{param_name}
    params_inputs = st.session_state.get('comfyflow_create_prompt_inputs', {})
    params_value = params_inputs[param]
    logger.debug(f"format_input_node_info, {param} {params_value}")
    node_id, class_type, param_name, param_value = params_value.split(NODE_SEP)
    return f"{node_id}:{class_type}:{param_name}:{param_value}"

def format_output_node_info(param):
    # format {id}.{class_type}
    params_outputs = st.session_state.get('comfyflow_create_prompt_outputs', {})
    params_value = params_outputs[param]
    logger.debug(f"format_output_node_info, {param} {params_value}")
    node_id, class_type, input_values = params_value.split(NODE_SEP)
    return f"{node_id}:{class_type}:{input_values}"

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
            file_name, _ = os.path.splitext(
                os.path.basename(image_upload.name))
            save_to_file = f'.comfyflow/temp/{datetime.today().strftime("%Y-%m-%d")}/{file_id}_{file_name}.png'

            os.makedirs(os.path.dirname(save_to_file), exist_ok=True)
            metadata = PngInfo()
            for x in tran_img.info:
                # logger.info(f"image meta data, {x}:{tran_img.info[x]}")
                # save as json file
                file_path = f'.comfyflow/temp/{datetime.today().strftime("%Y-%m-%d")}/{file_id}_{file_name}_{x}.json'
                with open(file_path, 'w') as json_file:
                    json_file.write(tran_img.info[x])

                # TODO: fix no metadata
                metadata.add_text(x, json.dumps(img.info[x]))
            logger.info(f"save image to {save_to_file} with meta data, {metadata}")
            img.save(save_to_file, format='png', PngInfo=metadata, compress_level=4)
            st.session_state['comfyflow_create_upload_image'] = save_to_file

        return tran_img.info
    except Exception as e:
        logger.error(f"process_workflow_meta error, {e}")
        return None


def parse_prompt(prompt_info):
    # parse prompt to inputs and outputs
    try:
        prompt = json.loads(prompt_info)
        params_inputs = {}
        params_outputs = {}
        for node_id in prompt:
            node = prompt[node_id]
            class_type = prompt[node_id]['class_type']
            node_inputs = []
            for param in node['inputs']:
                param_value = node['inputs'][param]
                option_key = f"{node_id}{NODE_SEP}{param}"
                option_value = f"{node_id}{NODE_SEP}{class_type}{NODE_SEP}{param}{NODE_SEP}{param_value}"
                logger.info(f"parse_prompt, {option_key} {option_value}")
                # check param_value is []
                if isinstance(param_value, list):
                    logger.info(f"ignore {option_key}, param_value is list, {param_value}")
                    continue
                if param == "choose file to upload":
                    logger.info(f"ignore {option_key}, param for 'choose file to upload'")
                    continue
                                
                params_inputs.update({option_key: option_value})
                node_inputs.append(param_value)

            is_output = st.session_state['comfy_object_info'][class_type]['output_node']
            if is_output:
                if class_type == 'SaveImage':
                    option_key = f"{node_id}{NODE_SEP}{class_type}"
                    if len(node_inputs) == 0:
                        option_value = f"{node_id}{NODE_SEP}{class_type}{NODE_SEP}None"
                    else:
                        option_value = f"{node_id}{NODE_SEP}{class_type}{NODE_SEP}{node_inputs}"
                    params_outputs.update({option_key: option_value})
                else:
                    logger.warning(f"Only support SaveImage as output node, {class_type}")

        return params_inputs, params_outputs
    except Exception as e:
        logger.error(f"parse_prompt error, {e}")
        return None, None


def process_image_change():
    logger.info(
        f"process_image_change session , {st.session_state['upload_image']}")
    if not st.session_state['upload_image']:
        logger.info("clear comfyflow_create_prompt, comfyflow_create_prompt_inputs and comfyflow_create_prompt_outputs")
        st.session_state['comfyflow_create_prompt'] = None
        st.session_state['comfyflow_create_prompt_inputs'] = {}
        st.session_state['comfyflow_create_prompt_outputs'] = {}


def get_node_input_config(input_param, app_input_name, app_input_description):
    params_inputs = st.session_state.get('comfyflow_create_prompt_inputs', {})
    option_params_value = params_inputs[input_param]
    logger.debug(f"get_node_input_config, {input_param} {option_params_value}")
    node_id, class_type, param, param_value = option_params_value.split(NODE_SEP)
    class_meta = st.session_state['comfy_object_info'][class_type]
    class_input = class_meta['input']['required']
    if 'optional' in class_meta['input'].keys():
        class_input.update(class_meta['input']['optional'])

    logger.info(f"{node_id} {class_type} {param} {param_value}, class input {class_input}")

    input_config = {}
    if isinstance(class_input[param][0], str):

        if class_input[param][0] == 'STRING':
            input_config = {
                "type": "TEXT",
                "name": app_input_name,
                "help": app_input_description,                 
                "default": str(param_value),
                "max": 300,
            }
        elif class_input[param][0] == 'INT':
            defaults = class_input[param][1]
            input_config = {
                "type": "NUMBER",
                "name": app_input_name,
                "help": app_input_description,
                "default": int(param_value),
                "min": defaults.get('min', 0),
                "max": min(defaults.get('max', 100), 4503599627370496),
                "step": defaults.get('step', 1),
            }
        elif class_input[param][0] == 'FLOAT':
            defaults = class_input[param][1]
            input_config = {
                "type": "NUMBER",
                "name": app_input_name,
                "help": app_input_description,
                "default": float(param_value),
                "min": defaults.get('min', 0),
                "max": min(defaults.get('max', 100), 4503599627370496),
                "step": defaults.get('step', 1),
            }
        elif class_input[param][0] == 'BOOLEAN':
            defaults = class_input[param][1]
            input_config = {
                "type": "CHECKBOX",
                "name": app_input_name,
                "help": app_input_description,
                "default": param_value,
            }
    elif isinstance(class_input[param][0], list):
        if class_type == 'LoadImage' and param == 'image':
            input_config = {
                "type": "UPLOADIMAGE",
                "name": app_input_name,
                "help": app_input_description,
            }
        else:
            input_config = {
                "type": "SELECT",
                "name": app_input_name,
                "help": app_input_description,
                "options": class_input[param][0],
            }
    return node_id, param, input_config


def get_node_output_config(output_param):
    params_outputs = st.session_state.get('comfyflow_create_prompt_outputs', {})
    output_param_value = params_outputs[output_param]
    node_id, class_type, param = output_param_value.split(NODE_SEP)
    output_param_inputs = {
        "outputs": {
        }
    }
    return node_id, output_param_inputs


def step1_upload_image(expanded=True):
    with st.expander("### :one: Upload image of comfyui workflow", expanded=expanded):
        image_col1, image_col2 = st.columns([0.5, 0.5])
        with image_col1:
            image_upload = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"], 
                                            key="upload_image", on_change=process_image_change, 
                                            help="upload image of comfyui workflow")

        with image_col2:
            if image_upload:
                metas = process_workflow_meta(image_upload, True)
                if metas and 'prompt' in metas.keys():
                    st.session_state['comfyflow_create_prompt'] = metas.get('prompt')
                    inputs, outputs = parse_prompt(metas.get('prompt'))
                    if inputs and outputs:
                        logger.info(f"comfyflow_create_prompt_inputs, {inputs}")
                        st.session_state['comfyflow_create_prompt_inputs'] = inputs
                        logger.info(f"comfyflow_create_prompt_outputs, {outputs}")
                        st.session_state['comfyflow_create_prompt_outputs'] = outputs

                        _, image_col, _ = st.columns([0.2, 0.6, 0.2])
                        with image_col:
                            st.image(image_upload, use_column_width=True,
                                     caption='ComfyUI Workflow Image, include workflow meta data')
                    else:
                        st.error(f"failed to parse comfyui workflow from image, please check up comfyui can run this workflow.")
                else:
                    st.error(f"this image don't contain comfyui workflow info.")


def step2_config_params(expanded=True):
    with st.expander("### :two: Config params of app", expanded=expanded):
        with st.container():
            name_col1, desc_col2 = st.columns([0.2, 0.8])
            with name_col1:
                st.text_input("App Name", value="", placeholder="input app name",
                              key="app_name", help="Input app name")
            with desc_col2:
                st.text_input("App Description", value="", placeholder="input app description",
                              key="app_desc", help="Input app description")

        with st.container():
            st.markdown("Input Params:")
            params_inputs = st.session_state.get('comfyflow_create_prompt_inputs', {})
            params_inputs_options = list(params_inputs.keys())
            param_input1_row = row([0.4, 0.2, 0.4], vertical_align="bottom")
            param_input1_row.selectbox("Select input of workflow", options=params_inputs_options, key="input_param1", format_func=format_input_node_info, index=None, help="Select a param from workflow")
            param_input1_row.text_input(
                "App Input Name", value="", placeholder="Param Name", key="input_param1_name", help="Input param name")
            param_input1_row.text_input("App Input Description", value="", placeholder="Param Description",
                                        key="input_param1_desc", help="Input param description")

            param_input2_row = row([0.4, 0.2, 0.4], vertical_align="bottom")
            param_input2_row.selectbox("Select input of workflow", options=params_inputs_options, key="input_param2", index=None, format_func=format_input_node_info, help="Select a param from workflow")
            param_input2_row.text_input(
                "App Input Name", value="", placeholder="Param Name", key="input_param2_name", help="Input param name")
            param_input2_row.text_input("App Input Description", value="", placeholder="Param Description",
                                        key="input_param2_desc", help="Input param description")

        with st.container():
            st.markdown("Output Params:")
            params_outputs = st.session_state.get('comfyflow_create_prompt_outputs', {})
            params_outputs_options = list(params_outputs.keys())
            param_output1_row = row([0.4, 0.2, 0.4], vertical_align="bottom")
            param_output1_row.selectbox("Select output of workflow", options=params_outputs_options,
                                        key="output_param1", format_func=format_output_node_info, help="Select a param from workflow")
            param_output1_row.text_input(
                "Apn Output Name", value="", placeholder="Param Name", key="output_param1_name",
                help="Input param name")
            param_output1_row.text_input("App Output Description", value="", placeholder="Param Description",
                                         key="output_param1_desc", help="Input param description")


def gen_app_config():
    prompt = st.session_state['comfyflow_create_prompt']
    input_param1 = st.session_state['input_param1']
    input_param1_name = st.session_state['input_param1_name']
    input_param1_desc = st.session_state['input_param1_desc']
    output_param1 = st.session_state['output_param1']
    app_name = st.session_state['app_name']
    app_desc = st.session_state['app_desc']
    logger.info(f"gen_app_config, {prompt} {input_param1} {output_param1} {app_name} {app_desc}")
    if prompt and input_param1 and output_param1 and app_name and app_desc:
        # gen and upload app.json
        app_config = {
            "name": app_name,
            "description": app_desc,
            "inputs": {},
            "outputs": {}
        }
        # parse input_param1
        node_id, param, input_param1_inputs = get_node_input_config(
            input_param1, input_param1_name, input_param1_desc)
        if node_id not in app_config['inputs'].keys():
            app_config['inputs'][node_id] = {"inputs": {}}
        app_config['inputs'][node_id]['inputs'][param] = input_param1_inputs

        # parse input_param2
        input_param2 = st.session_state['input_param2']
        input_param2_name = st.session_state['input_param2_name']
        input_param2_desc = st.session_state['input_param2_desc']
        if input_param2:
            node_id, param, input_param2_inputs = get_node_input_config(
                input_param2, input_param2_name, input_param2_desc)
            if node_id not in app_config['inputs'].keys():
                app_config['inputs'][node_id] = {"inputs": {}}
            app_config['inputs'][node_id]['inputs'][param] = input_param2_inputs

        # parse output_param1
        node_id, output_param1_inputs = get_node_output_config(output_param1)
        app_config['outputs'][node_id] = output_param1_inputs
        return app_config


def submit_app(app_config):
    # check app dir
    workflow_path = f'.comfyflow/workflows/{st.session_state["app_name"]}'
    os.makedirs(workflow_path, exist_ok=True)

    # save app config
    app_file_path = f'{workflow_path}/app.json'
    with open(app_file_path, 'w') as f:
        # logger.info(f"save app config to {app_file_path}, {app_config}")
        json.dump(app_config, f)

    # upload prompt.json
    prompt_file_path = f'{workflow_path}/prompt.json'
    with open(prompt_file_path, 'w') as f:
        prompt = st.session_state['comfyflow_create_prompt']
        # logger.info(f"save prompt to {prompt_file_path}, {prompt}")
        f.write(prompt)

    # upload workflow image
    upload_image = st.session_state['comfyflow_create_upload_image']
    image_file_path = f'{workflow_path}/app.png'
    os.rename(upload_image, image_file_path)

    # submit to sqlite
    from modules.sqlitehelper import sqlitehelper
    app = {}
    app['name'] = app_config['name']
    app['description'] = app_config['description']
    app['app_conf'] = json.dumps(app_config)
    app['api_conf'] = prompt
    app['status'] = 'created'
    app['image'] = open(image_file_path, 'rb').read()
    sqlitehelper.create_app(app)


with st.container():
    st.title("🌱 Create app from comfyui workflow")

    # upload workflow image and config params
    step1_upload_image()
    step2_config_params()

    with stylable_container(
        key="submit_button",
        css_styles="""
            button {
                background-color: rgb(28 131 225);
                color: white;
                border-radius: 4px;
            }
            button:hover, button:focus {
                border: 0px solid rgb(28 131 225);
            }
            button:
        """,
    ):
        submit_button = st.button(
            "Submit", key='submit_workflow', use_container_width=True, help="Submit app params")
        if submit_button:
            app_config = gen_app_config()
            if app_config:
                submit_app(app_config=app_config)
                st.success(f"Submit app successfully, {app_config['name']}")
            else:
                st.error(
                    "Submit app failed, please check workflow image and config params")
