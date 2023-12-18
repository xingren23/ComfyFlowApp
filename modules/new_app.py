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
FAQ_URL = "https://github.com/xingren23/ComfyFlowApp/wiki/FAQ"

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


def parse_prompt(prompt_info, object_info_meta):
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

            is_output = object_info_meta[class_type]['output_node']
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

        return (params_inputs, params_outputs)
    except Exception as e:
        st.error(f"parse_prompt error, {e} refer to {FAQ_URL}")
        return (None, None)


def process_image_change():
    comfyui_object_info = st.session_state.get('comfyui_object_info')
    upload_image = st.session_state['create_upload_image']
    if upload_image:
        metas = process_workflow_meta(upload_image)
        if metas and 'prompt' in metas.keys() and 'workflow' in metas.keys():
            st.session_state['create_prompt'] = metas.get('prompt')
            st.session_state['create_workflow'] = metas.get('workflow')
            inputs, outputs = parse_prompt(metas.get('prompt'), comfyui_object_info)
            if inputs:
                logger.info(f"create_prompt_inputs, {inputs}")
                st.success(f"parse inputs from workflow image, input nodes {len(inputs)}")
                st.session_state['create_prompt_inputs'] = inputs
            else:
                st.error(f"parse workflow from image error, inputs is None, refer to {FAQ_URL}")

            if outputs:
                logger.info(f"create_prompt_outputs, {outputs}")
                st.success(f"parse outputs from workflow image, output nodes {len(outputs)}")
                st.session_state['create_prompt_outputs'] = outputs
            else:
                st.error(f"parse workflow from image error, outputs is None, refer to {FAQ_URL}")
            
        else:
            st.error(f"the image don't contain workflow info, refer to {FAQ_URL}")
    else:
        st.session_state['create_prompt'] = None
        st.session_state['create_workflow'] = None
        st.session_state['create_prompt_inputs'] = {}
        st.session_state['create_prompt_outputs'] = {}

def process_image_edit(api_prompt):
    comfyui_object_info = st.session_state.get('comfyui_object_info')
    if api_prompt:
        st.session_state['create_prompt'] =api_prompt
        inputs, outputs = parse_prompt(api_prompt, comfyui_object_info)
        if inputs:
            logger.info(f"create_prompt_inputs, {inputs}")
            st.success(f"parse inputs from workflow image, input nodes {len(inputs)}")
            st.session_state['create_prompt_inputs'] = inputs
        else:
            st.error(f"parse workflow from image error, inputs is None, refer to {FAQ_URL}")

        if outputs:
            logger.info(f"create_prompt_outputs, {outputs}")
            st.success(f"parse outputs from workflow image, output nodes {len(outputs)}")
            st.session_state['create_prompt_outputs'] = outputs
        else:
            st.error(f"parse workflow from image error, outputs is None, refer to {FAQ_URL}")
    else:
        st.error(f"the image don't contain workflow info, refer to {FAQ_URL}")
        

def get_node_input_config(input_param, app_input_name, app_input_description):
    params_inputs = st.session_state.get('create_prompt_inputs', {})
    option_params_value = params_inputs[input_param]
    logger.debug(f"get_node_input_config, {input_param} {option_params_value}")
    node_id, class_type, param, param_value = option_params_value.split(NODE_SEP)
    comfyui_object_info = st.session_state.get('comfyui_object_info')
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
                "max": 500,
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

        # parse input_param3
        input_param3 = st.session_state['input_param3']
        input_param3_name = st.session_state['input_param3_name']
        input_param3_desc = st.session_state['input_param3_desc']
        if input_param3:
            node_id, param, input_param3_inputs = get_node_input_config(
                input_param3, input_param3_name, input_param3_desc)
            if node_id not in app_config['inputs'].keys():
                app_config['inputs'][node_id] = {"inputs": {}}
            app_config['inputs'][node_id]['inputs'][param] = input_param3_inputs

        # parse output_param1
        node_id, output_param1_inputs = get_node_output_config(output_param1)
        app_config['outputs'][node_id] = output_param1_inputs
        return app_config


def submit_app():
    app_config = gen_app_config()
    if app_config:
        # check user login
        if not st.session_state.get('username'):
            st.warning("Please go to homepage for your login :point_left:")
            st.stop()

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
            app['workflow_conf'] = st.session_state['create_workflow']
            app['status'] = 'created'
            app['template'] = 'default'
            app['image'] = img_bytesio.getvalue()
            app['username'] = st.session_state['username']
            get_workspace_model().create_app(app)

            logger.info(f"submit app successfully, {app_config['name']}")
            st.session_state['create_submit_info'] = "success"
    else:
        logger.info(f"submit app error, {app_config['name']}")
        st.session_state['create_submit_info'] = "error"

def save_app(app):
    app_config = gen_app_config()
    if app_config:
        get_workspace_model().edit_app(app.id, app_config['name'], app_config['description'], 
                                       json.dumps(app_config))

        logger.info(f"save app successfully, {app_config['name']}")
        st.session_state['save_submit_info'] = "success"
    else:
        logger.info(f"save app error, {app_config['name']}")
        st.session_state['save_submit_info'] = "error"

def check_app_name():
    app_name_text = st.session_state['create_app_name']
    app = get_workspace_model().get_app(app_name_text)
    if app:
        st.session_state['create_exist_app_name'] = True
    else:
        st.session_state['create_exist_app_name'] = False

def on_edit_workspace():
    st.session_state.pop('edit_app', None)
    logger.info("back to workspace")

def edit_app_ui(app):
    with page.stylable_button_container():
        header_row = row([0.85, 0.15], vertical_align="top")
        header_row.title("🌱 Edit app from comfyui workflow")
        header_row.button("Back Workspace", help="Back to your workspace", key="edit_back_workspace", on_click=on_edit_workspace)
        
    try:
        comfyui_object_info = get_comfyui_object_info()
        st.session_state['comfyui_object_info'] = comfyui_object_info
    except Exception as e:
        st.error(f"connect to comfyui node error, {e}")
        st.stop()

    # upload workflow image and config params
    with st.expander("### :one: Upload image of comfyui workflow", expanded=True):
        image_col1, image_col2 = st.columns([0.5, 0.5])

        process_image_edit(app.api_conf)
       
        with image_col2:
            image_icon = BytesIO(app.image)
            input_params = st.session_state.get('create_prompt_inputs')
            output_params = st.session_state.get('create_prompt_outputs')
            if image_icon and input_params and output_params:
                logger.debug(f"input_params: {input_params}, output_params: {output_params}")
                _, image_col, _ = st.columns([0.2, 0.6, 0.2])
                with image_col:
                    st.image(image_icon, use_column_width=True, caption='ComfyUI Image with workflow info')
            else:
                st.warning("Can't load comfyui workflow image")
                
             
    with st.expander("### :two: Config params of app", expanded=True):
        app_conf = json.loads(app.app_conf)

        with st.container():
            name_col1, desc_col2 = st.columns([0.2, 0.8])
            with name_col1:
                st.text_input("App Name *", value=app.name, placeholder="input app name",
                              key="create_app_name", help="Input app name")    

            with desc_col2:
                st.text_input("App Description *", value=app.description, placeholder="input app description",
                              key="create_app_description", help="Input app description")

        with st.container():
            
            st.markdown("Input Params:")
            params_inputs = st.session_state.get('create_prompt_inputs', {})
            params_inputs_options = list(params_inputs.keys())
            
            input_params = []
            for node_id in app_conf['inputs']:
                node_inputs = app_conf['inputs'][node_id]['inputs']
                for param in node_inputs:
                    param_name = node_inputs[param]['name']
                    param_help = node_inputs[param]['help']

                    param = {
                        'index': f"{node_id}{NODE_SEP}{param}",
                        'name': param_name,
                        'help': param_help,
                    }
                    input_params.append(param)

            logger.info(f"params_inputs_options {params_inputs_options}, input_params: {input_params}")
            
            if len(input_params) > 0:
                input_param = input_params[0]
                add_input_config_param(params_inputs_options, 1, input_param)
            else:
                add_input_config_param(params_inputs_options, 1, None)

            if len(input_params) > 1:
                input_param_2 = input_params[1]
                add_input_config_param(params_inputs_options, 2, input_param_2)
            else:
                add_input_config_param(params_inputs_options, 2, None)
            
            if len(input_params) > 2:
                input_param_3 = input_params[2]
                add_input_config_param(params_inputs_options, 3, input_param_3)
            else:
                add_input_config_param(params_inputs_options, 3, None)

        with st.container():
            
            st.markdown("Output Params:")
            params_outputs = st.session_state.get('create_prompt_outputs', {})
            params_outputs_options = list(params_outputs.keys())

            output_params = []
            for node_id in app_conf['outputs']:
                node_inputs = app_conf['outputs'][node_id]['outputs']
                for param in node_inputs:
                    param_name = node_inputs[param]['name']
                    param_help = node_inputs[param]['help']

                    param = {
                        'index': f"{node_id}{NODE_SEP}{param}",
                        'name': param_name,
                        'help': param_help,
                    }
                    input_params.append(param)

            if len(output_params) > 0:
                output_param_1 = output_params[0]
                add_output_config_param(params_outputs_options, 1, output_param_1)
            else:
                add_output_config_param(params_outputs_options, 1, None)

    with st.container():
        operation_row = row([0.15, 0.7, 0.15])
        submit_button = operation_row.button("Save", key='edit_submit_app', type="primary",
                                            use_container_width=True, 
                                            help="Save app params",on_click=save_app, args=(app,))     
        if submit_button:
            submit_info = st.session_state.get('save_submit_info')
            if submit_info == 'success':
                st.success("Save app successfully, back your workspace")
                st.stop()
            else:
                st.error(f"Save app error, please check up app params, refer to {FAQ_URL}")

        operation_row.empty()
        next_placeholder = operation_row.empty()

def on_new_workspace():
    st.session_state.pop('new_app', None)
    logger.info("back to workspace")

def add_input_config_param(params_inputs_options, index, input_param):
    if not input_param:
        input_param = {
            'name': None,
            'help': None,
        }
        option_index = None
    else:
        option_index = params_inputs_options.index(input_param['index'])

    param_input_row = row([0.4, 0.2, 0.4], vertical_align="bottom")
    param_input_row.selectbox("Select input of workflow *", options=params_inputs_options, key=f"input_param{index}", 
                            index=option_index,format_func=format_input_node_info, help="Select a param from workflow")
    param_input_row.text_input("App Input Name *", placeholder="Param Name", key=f"input_param{index}_name", 
                               value=input_param['name'], help="Input param name")
    param_input_row.text_input("App Input Description", value=input_param['help'], placeholder="Param Description",
                                key=f"input_param{index}_desc", help="Input param description")
    
def add_output_config_param(params_outputs_options, index, output_param):
    if not output_param:
        output_param = {
            'name': None,
            'help': None,
        }
        option_index = None
    else:
        option_index = params_outputs_options.index(output_param['index'])
    
    param_output_row = row([0.4, 0.2, 0.4], vertical_align="bottom")
    param_output_row.selectbox("Select output of workflow *", options=params_outputs_options,
                            key=f"output_param{index}", index=option_index, format_func=format_output_node_info, help="Select a param from workflow")
    param_output_row.text_input("Apn Output Name *", placeholder="Param Name", key=f"output_param{index}_name", 
                                value=output_param['name'],help="Input param name")
    param_output_row.text_input("App Output Description", value=output_param['help'], placeholder="Param Description",
                                key=f"output_param{index}_desc", help="Input param description")

def new_app_ui():
    logger.info("Loading create page")
    with page.stylable_button_container():
        header_row = row([0.85, 0.15], vertical_align="top")
        header_row.title("🌱 Create app from comfyui workflow")
        header_row.button("Back Workspace", help="Back to your workspace", key="create_back_workspace", on_click=on_new_workspace)

        # check user login
        if not st.session_state.get('username'):
            st.warning("Please go to homepage for your login :point_left:")
            st.stop()

    try:
        comfyui_object_info = get_comfyui_object_info()
        st.session_state['comfyui_object_info'] = comfyui_object_info
    except Exception as e:
        st.error(f"connect to comfyui node error, {e}")
        st.stop()

    # upload workflow image and config params
    with st.expander("### :one: Upload image of comfyui workflow", expanded=True):
        image_col1, image_col2 = st.columns([0.5, 0.5])
        with image_col1:
            st.file_uploader("Upload image from comfyui outputs *", type=["png", "jpg", "jpeg"], 
                                            key="create_upload_image", 
                                            help="upload image from comfyui output folder", accept_multiple_files=False)
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
                st.text_input("App Name *", value="", placeholder="input app name",
                              key="create_app_name", help="Input app name")    

            with desc_col2:
                st.text_input("App Description *", value="", placeholder="input app description",
                              key="create_app_description", help="Input app description")

        with st.container():
            st.markdown("Input Params:")
            params_inputs = st.session_state.get('create_prompt_inputs', {})
            params_inputs_options = list(params_inputs.keys())

            add_input_config_param(params_inputs_options, 1, None)
            add_input_config_param(params_inputs_options, 2, None)
            add_input_config_param(params_inputs_options, 3, None)
        with st.container():
            st.markdown("Output Params:")
            params_outputs = st.session_state.get('create_prompt_outputs', {})
            params_outputs_options = list(params_outputs.keys())

            add_output_config_param(params_outputs_options, 1, None)
            
    
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
                st.error(f"Submit app error, please check up app params, refer to {FAQ_URL}")

        operation_row.empty()

        next_placeholder = operation_row.empty()