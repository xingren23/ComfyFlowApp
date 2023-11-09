from loguru import logger
from PIL import Image, ImageOps
from io import BytesIO
import json
import streamlit as st
import modules.page as page
from streamlit_extras.row import row
from streamlit_extras.switch_page_button import switch_page
from modules import get_comfyui_object_info, get_workspace_model

NODE_SEP = '||'

def format_input_node_info(param):
    # format {id}.{class_type}.{alias}.{param_name}
    params_inputs = st.session_state.get('create_prompt_inputs', {})
    params_value = params_inputs[param]
    logger.debug(f"format_input_node_info, {param} {params_value}")
    node_id, class_type, param_name, param_value = params_value.split(NODE_SEP)
    return f"{node_id}:{class_type}:{param_name}:{param_value}"

def format_output_node_info(param):
    # format {id}.{class_type}
    params_outputs = st.session_state.get('create_prompt_outputs', {})
    params_value = params_outputs[param]
    logger.debug(f"format_output_node_info, {param} {params_value}")
    node_id, class_type, input_values = params_value.split(NODE_SEP)
    return f"{node_id}:{class_type}:{input_values}"

def process_workflow_meta(image_upload):
    # parse meta data from image, save image to local
    try:
        logger.info(f"process_workflow_meta, {image_upload}")
        img = Image.open(image_upload)
        tran_img = ImageOps.exif_transpose(img)
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
                logger.debug(f"parse_prompt, {option_key} {option_value}")
                # check param_value is []
                if isinstance(param_value, list):
                    logger.debug(f"ignore {option_key}, param_value is list, {param_value}")
                    continue
                if param == "choose file to upload":
                    logger.debug(f"ignore {option_key}, param for 'choose file to upload'")
                    continue
                                
                params_inputs.update({option_key: option_value})
                node_inputs.append(param_value)

            is_output = get_comfyui_object_info()[class_type]['output_node']
            if is_output:
                # TODO: support multi output
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
    upload_image = st.session_state['create_upload_image']
    if upload_image:
        metas = process_workflow_meta(upload_image)
        if metas and 'prompt' in metas.keys():
            st.session_state['create_prompt'] = metas.get('prompt')
            inputs, outputs = parse_prompt(metas.get('prompt'))
            if inputs and outputs:
                logger.info(f"create_prompt_inputs, {inputs}")
                st.session_state['create_prompt_inputs'] = inputs

                logger.info(f"create_prompt_outputs, {outputs}")
                st.session_state['create_prompt_outputs'] = outputs 

                st.success("parse workflow from image successfully")
            else:
                st.error("parse workflow from image error, please check up comfyui is alive and can run this workflow.")
        else:
            st.error("the image don't contain workflow info")
    else:
        st.session_state['create_prompt'] = None
        st.session_state['create_prompt_inputs'] = {}
        st.session_state['create_prompt_outputs'] = {}
        

def get_node_input_config(input_param, app_input_name, app_input_description):
    params_inputs = st.session_state.get('create_prompt_inputs', {})
    option_params_value = params_inputs[input_param]
    logger.debug(f"get_node_input_config, {input_param} {option_params_value}")
    node_id, class_type, param, param_value = option_params_value.split(NODE_SEP)
    comfyui_object_info = get_comfyui_object_info()
    class_meta = comfyui_object_info[class_type]
    class_input = class_meta['input']['required']
    if 'optional' in class_meta['input'].keys():
        class_input.update(class_meta['input']['optional'])

    logger.debug(f"{node_id} {class_type} {param} {param_value}, class input {class_input}")

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
    params_outputs = st.session_state.get('create_prompt_outputs', {})
    output_param_value = params_outputs[output_param]
    node_id, class_type, param = output_param_value.split(NODE_SEP)
    output_param_inputs = {
        "outputs": {
        }
    }
    return node_id, output_param_inputs

    
def gen_app_config():
    prompt = st.session_state['create_prompt']
    input_param1 = st.session_state['input_param1']
    input_param1_name = st.session_state['input_param1_name']
    input_param1_desc = st.session_state['input_param1_desc']
    output_param1 = st.session_state['output_param1']
    app_name = st.session_state['create_app_name']
    app_description = st.session_state['create_app_description']
    logger.info(f"gen_app_config, {prompt} {input_param1} {output_param1} {app_name} {app_description}")
    if prompt and input_param1 and output_param1 and app_name and app_description:
        # gen and upload app.json
        app_config = {
            "name": app_name,
            "description": app_description,
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


def submit_app():
    app_config = gen_app_config()
    if app_config:
        # submit to sqlite
        if get_workspace_model().get_app(app_config['name']):
            st.session_state['create_submit_info'] = "exist"
        else:
            # resize image
            img = Image.open(st.session_state['create_upload_image'])
            img = img.resize((64,64))
            img_bytesio = BytesIO()
            img.save(img_bytesio, format="PNG")
            
            app = {}
            app['name'] = app_config['name']
            app['description'] = app_config['description']
            app['app_conf'] = json.dumps(app_config)
            app['api_conf'] = st.session_state['create_prompt']
            app['status'] = 'created'
            app['template'] = 'default'
            app['image'] = img_bytesio.getvalue()
            get_workspace_model().create_app(app)

            logger.info(f"submit app successfully, {app_config['name']}")
            st.session_state['create_submit_info'] = "success"
    else:
        logger.info(f"submit app error, {app_config['name']}")
        st.session_state['create_submit_info'] = "error"

def check_app_name():
    app_name_text = st.session_state['create_app_name']
    app = get_workspace_model().get_app(app_name_text)
    if app:
        st.session_state['create_exist_app_name'] = True
    else:
        st.session_state['create_exist_app_name'] = False

def on_new_workspace():
    st.session_state['new_app'] = False

def new_app_ui():
    logger.info("Loading create page")
    with page.stylable_button_container():
        header_row = row([0.85, 0.15], vertical_align="top")
        header_row.title("🌱 Create app from comfyui workflow")
        header_row.button("Back Workspace", help="Back to your workspace", key="create_back_workspace", on_click=on_new_workspace)
        

    # upload workflow image and config params
    with st.expander("### :one: Upload image of comfyui workflow", expanded=True):
        image_col1, image_col2 = st.columns([0.5, 0.5])
        with image_col1:
            image_uploader = st.file_uploader("Upload image *", type=["png", "jpg", "jpeg"], 
                                            key="create_upload_image", 
                                            help="upload image of comfyui workflow")
            process_image_change()  

        with image_col2:
            image_upload = st.session_state.get('create_upload_image')
            input_params = st.session_state.get('create_prompt_inputs')
            output_params = st.session_state.get('create_prompt_outputs')
            if image_upload and input_params and output_params:
                logger.debug(f"input_params: {input_params}, output_params: {output_params}")
                _, image_col, _ = st.columns([0.2, 0.6, 0.2])
                with image_col:
                    st.image(image_upload, use_column_width=True, caption='ComfyUI Image with workflow info')
                
                
    with st.expander("### :two: Config params of app", expanded=True):
        with st.container():
            name_col1, desc_col2 = st.columns([0.2, 0.8])
            with name_col1:
                app_name_text = st.text_input("App Name *", value="", placeholder="input app name",
                              key="create_app_name", help="Input app name")    

            with desc_col2:
                st.text_input("App Description *", value="", placeholder="input app description",
                              key="create_app_description", help="Input app description")

        with st.container():
            st.markdown("Input Params:")
            params_inputs = st.session_state.get('create_prompt_inputs', {})
            params_inputs_options = list(params_inputs.keys())

            param_input1_row = row([0.4, 0.2, 0.4], vertical_align="bottom")
            param_input1_row.selectbox("Select input of workflow *", options=params_inputs_options, key="input_param1", format_func=format_input_node_info, index=None, help="Select a param from workflow")
            param_input1_row.text_input(
                "App Input Name *", value="", placeholder="Param Name", key="input_param1_name", help="Input param name")
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
            params_outputs = st.session_state.get('create_prompt_outputs', {})
            params_outputs_options = list(params_outputs.keys())
            param_output1_row = row([0.4, 0.2, 0.4], vertical_align="bottom")
            param_output1_row.selectbox("Select output of workflow *", options=params_outputs_options,
                                        key="output_param1", format_func=format_output_node_info, help="Select a param from workflow")
            param_output1_row.text_input(
                "Apn Output Name *", value="", placeholder="Param Name", key="output_param1_name",
                help="Input param name")
            param_output1_row.text_input("App Output Description", value="", placeholder="Param Description",
                                         key="output_param1_desc", help="Input param description")
            
    
    with st.container():
        operation_row = row([0.15, 0.7, 0.15])
        submit_button = operation_row.button("Submit", key='create_submit_app', type="primary",
                                            use_container_width=True, 
                                            help="Submit app params",on_click=submit_app)     
        if submit_button:
            submit_info = st.session_state.get('create_submit_info')
            if submit_info == 'success':
                st.success("Submit app successfully, back your workspace or preview this app")
                st.stop()
            elif submit_info == 'exist':
                st.error("Submit app error, app name has existed")
            else:
                st.error("Submit app error, please check up app params")

        operation_row.empty()

        next_placeholder = operation_row.empty()