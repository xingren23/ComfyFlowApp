from loguru import logger
import json
import os
import base64
import requests
import streamlit as st
import modules.page as page
from modules.workspace_model import AppStatus
from streamlit_extras.row import row

MODEL_SEP = '##'
comfyui_supported_pt_extensions = set(['.ckpt', '.pt', '.bin', '.pth', '.safetensors'])

@st.cache_data(ttl=60*60)
def get_comfyflow_object_info(cookies):
    comfyflow_api = os.getenv('COMFYFLOW_API_URL')
    # request comfyflow object info
    object_info = requests.get(f"{comfyflow_api}/api/comfyflow/object_info", cookies=cookies)
    if object_info.status_code != 200:
        logger.error(f"Get comfyflow object info failed, {object_info.text} {cookies}")
        st.session_state['get_comfyflow_object_info_error'] = f"Get comfyflow object info failed, {object_info.text}"
        return None
    logger.info(f"get_comfyflow_object_info, {object_info}")
    return object_info.json()

@st.cache_data(ttl=60*60)
def get_comfyflow_model_info(cookies):
    comfyflow_api = os.getenv('COMFYFLOW_API_URL')
    # request comfyflow object info
    model_info = requests.get(f"{comfyflow_api}/api/comfyflow/model_info", cookies=cookies)
    if model_info.status_code != 200:
        logger.error(f"Get comfyflow model info failed, {model_info.text}")
        st.session_state['get_comfyflow_model_info_error'] = f"Get comfyflow model info failed, {model_info.text}"
        return None
    logger.info(f"get_comfyflow_model_info, {model_info}")
    return model_info.json() 

def do_submit_comfyflow_missing(data, cookies):
    comfyflow_api = os.getenv('COMFYFLOW_API_URL')
    # request comfyflow missing
    ret = requests.post(f"{comfyflow_api}/api/comfyflow/missing", json=data, cookies=cookies)
    if ret.status_code != 200:
        logger.error(f"Submit comfyflow missing failed, {ret.text}")
        st.error(f"Submit comfyflow missing failed, {ret.text}")
        return None
    
    st.success(f"submit comfyflow missing success, thanks for your feedback.")
    return ret.json()

def do_publish_app(name, description, image, app_conf, api_conf, workflow_conf, endpoint, template, status, cookies=None):
    comfyflow_api = os.getenv('COMFYFLOW_API_URL')
    # post app to comfyflow.app
    app = {
        "name": name,
        "description": description,
        "image": image,
        "app_conf": app_conf,
        "api_conf": api_conf,
        "workflow_conf": workflow_conf,
        "endpoint": endpoint,
        "template": template,
        "status": status
    }
    ret = requests.post(f"{comfyflow_api}/api/app/publish", json=app, cookies=cookies)
    if ret.status_code != 200:
        logger.error(f"publish app failed, {name} {ret.content}")
        st.error(f"publish app failed, {name} {ret.content}")
        return ret
    else:
        logger.info(f"publish app success, {name}")
        st.success(f"publish app success, {name}, you could preview and modify on https://comfyflow.app")
        return ret

def on_publish_workspace():
    st.session_state.pop('publish_app', None)
    logger.info("back to workspace")

def is_comfyui_model_path(model_path):
    for ext in comfyui_supported_pt_extensions:
        if isinstance(model_path, str) and model_path.endswith(ext):
            return True
    return False


def publish_app_ui(app, cookies):
    logger.info("Loading publish page")

    with page.stylable_button_container():
        header_row = row([0.85, 0.15], vertical_align="top")
        header_row.title("✈️ Publish app")
        header_row.button("Back Workspace", help="Back to your workspace", key='publish_back_workspace', on_click=on_publish_workspace)

        # check user login
        if not st.session_state.get('username'):
            st.warning("Please go to homepage for your login :point_left:")
            st.stop()

    with st.container():
        api_data_json = json.loads(app.api_conf)
        app_data_json = json.loads(app.app_conf)
        
        # get comfyflow object info
        comfyflow_object_info = get_comfyflow_object_info(cookies)
        if not comfyflow_object_info:
            st.error(f"Failed to get comfyflow object info, please check comfyflow node.")
            st.stop()

       
        # parse app nodes
        missing_nodes = []
        with st.expander("Parse comfyui node info", expanded=True):
            for node_id in api_data_json:
                inputs = api_data_json[node_id]['inputs']
                # check node type                   
                class_type = api_data_json[node_id]['class_type']
                if class_type in comfyflow_object_info:
                    st.write(f":green[Check node info\, {node_id}\:{class_type}]")
                else:
                    st.write(f":red[Node info not found\, {node_id}\:{class_type}]")
                    missing_nodes.append(class_type)
                    
        # parse app models
        missing_models = []
        with st.expander("Parse comfyui model info", expanded=True):
            for node_id in api_data_json:
                inputs = api_data_json[node_id]['inputs']
                class_type = api_data_json[node_id]['class_type']
                # check model path
                logger.debug(f"inputs, {inputs}")    
                for key, value in inputs.items():
                    try:
                        if isinstance(value, str):
                            if is_comfyui_model_path(value):
                                if key in comfyflow_object_info[class_type]['input']['required']:
                                    model_options = comfyflow_object_info[class_type]['input']['required'][key][0]
                                elif key in comfyflow_object_info[class_type]['input']['optional']:
                                    model_options = comfyflow_object_info[class_type]['input']['optional'][key][0]
                                else:
                                    model_options = []

                                if value not in model_options:
                                    st.write(f":blue[Invalid model path\, {value}]")
                                    missing_models.append({class_type: value})
                                else:
                                    st.write(f":green[Check model path\, {value}]")
                        elif isinstance(value, dict):
                            for k, v in value.items():
                                if is_comfyui_model_path(v):
                                    st.write(f":green[ignore path\, {k} {value}]")
                                    
                    except Exception as e:
                        st.write(f":blue[Invalid model path\, {value}]")
                        missing_models.append({class_type: value})

        with st.container():
            operation_row = row([3, 6.2, 0.8])

            missing_button = operation_row.button("Request missing nodes and models", key='missing_button', 
                      help="Request missing comfyui custom nodes and models", disabled=len(missing_nodes) == 0 and len(missing_models) == 0)
            if missing_button:
                # request comfyui custom nodes and models
                data = {
                    'app_id': app.id,
                    'missing': json.dumps({
                        'nodes': missing_nodes,
                        'models': missing_models
                    })
                }
                do_submit_comfyflow_missing(data, cookies)
        
            operation_row.write("")

            publish_button = operation_row.button("Publish", key='publish_button', type='primary', 
                        help="Publish app to https://comfyflow.app", disabled=len(missing_nodes) > 0)
            if publish_button:
                # convert image to base64
                image_base64 = base64.b64encode(app.image).decode('utf-8')
                # call api to publish app
                do_publish_app(app.name, app.description, image_base64, app.app_conf, app.api_conf, app.workflow_conf, "", app.template, AppStatus.PUBLISHED.value, cookies)
