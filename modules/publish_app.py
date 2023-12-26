from loguru import logger
import json
import os
import base64
import requests
from urllib.parse import urlparse, parse_qs
import streamlit as st
import modules.page as page
from modules import get_workspace_model
from modules.workspace_model import AppStatus
from streamlit_extras.row import row
from huggingface_hub import hf_hub_url, get_hf_file_metadata

MODEL_SEP = '##'
comfyui_supported_pt_extensions = set(['.ckpt', '.pt', '.bin', '.pth', '.safetensors'])

@st.cache_data(ttl=24*60*60)
def get_huggingface_model_meta(model_url):
    # get model info from download url, 
    # eg: https://huggingface.co/segmind/SSD-1B/blob/main/unet/diffusion_pytorch_model.fp16.safetensors
    hf_meta = get_hf_file_metadata(url=model_url)
    logger.debug(f"hf_meta, {hf_meta}")
    return hf_meta
        
@st.cache_data(ttl=60*60)        
def get_civitai_model_meta(model_version_url):
    """
    model_url: https://civitai.com/models/113362?modelVersionId=159291
    api: https://github.com/civitai/civitai/wiki/REST-API-Reference#get-apiv1models-versionsmodelversionid
    """
    parsed_url = urlparse(model_version_url)
    model_id = parsed_url.path.split('/')[-1]
    model_version_id = parse_qs(parsed_url.query)['modelVersionId'][0]
    ret = requests.get(f"https://civitai.com/api/v1/model-versions/{model_version_id}")
    if ret.status_code != 200:
        raise Exception(f"Failed to get model meta for {model_version_url}")
    ret_json = ret.json()
    assert str(model_id) == str(ret_json["modelId"])
    model_meta = {}
    # name
    model_meta["id"] = model_id
    # enum (Checkpoint, TextualInversion, Hypernetwork, AestheticGradient, LORA, Controlnet, Poses)
    # modelVersions
    model_meta["download_url"] = ret_json["downloadUrl"]
    model_meta['model'] = ret_json["model"]
    model_meta['files'] = ret_json["files"]
    return model_meta


@st.cache_data(ttl=60*60)
def get_model_meta(model_url):
    """
    return model meta, eg: {'download_url': 'xxx', 'size': 123}
    """
    if model_url.startswith("https://huggingface.co"):
        hf_meta = get_huggingface_model_meta(model_url)
        meta = {}
        meta['model_url'] = model_url
        meta['size'] = hf_meta.size
        return meta
    elif model_url.startswith("https://civitai.com"):
        civitai_meta = get_civitai_model_meta(model_url)
        civitai_meta['model_url'] = model_url
        civitai_meta['size'] = civitai_meta['files'][0]['sizeKB'] * 1024
        return civitai_meta

@st.cache_data(ttl=60*60)
def get_endpoint_object_info():
    endpoint_opt = st.session_state.get('publish_endpoint', None)
    if not endpoint_opt:
        st.session_state['endpoint_object_info'] = None
        return
    
    endpoint = endpoint_opt.split('\t')[1]
    object_info_url = f"{endpoint}/object_info"
    ret = requests.get(object_info_url)
    if ret.status_code != 200:
        logger.error(f"Failed to get comfyui {object_info_url}, {ret.content}")
        st.session_state['endpoint_object_info'] = None
    else:
        st.session_state['endpoint_object_info'] = ret.json()


def get_node_all(session_cookie):
    api_url = f'{os.environ.get("COMFYFLOW_API_URL")}/api/node/all' 
    req = requests.get(api_url, cookies=session_cookie)
    if req.status_code == 200:
        logger.info(f"get all node list, {req.json()}")
        return req.json()
    else:
        return None

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
        logger.info(f"publish app success, {name}， please preview on https://comfyflow.app")
        st.success(f"publish app success, {name},  please preview on https://comfyflow.app")
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
        header_row.title("✈️ Publish comfyflow app")
        header_row.button("Back Workspace", help="Back to your workspace", key='publish_back_workspace', on_click=on_publish_workspace)

        # check user login
        if not st.session_state.get('username'):
            st.warning("Please go to homepage for your login :point_left:")
            st.stop()

    with st.container():
        app_name = app.name
        api_data_json = json.loads(app.api_conf)
        app_data_json = json.loads(app.app_conf)
        
        # select endpoint
        nodes = get_node_all(cookies) 
        if not nodes:
            st.info("No comfyui node found, manage your comfyui node on website: https://comfyflow.app ")
            st.stop()

        endpoint_options = []
        for pool_name, pool in nodes.items():
            if pool_name == 'common':
                tag = 'Common Comfyui Instances'
            elif pool_name == 'mine':
                tag = 'Mine Comfyui Instances'
            else:
                tag = 'Other Comfyui Instances'
            for node in pool:
                endpoint_options.append(f"[{tag}]\t{node['endpoint']}\t")
        endpoint = st.selectbox(":red[Select endpoint]", endpoint_options, placeholder="Choose a ComfyUI Instance...", key='publish_endpoint', index=None, help="Select endpoint to publish app", on_change=get_endpoint_object_info)
        if not endpoint:
            st.stop()

        # get endpoint object info
        endpoint_object_info = st.session_state.get('endpoint_object_info', None)
        if not endpoint_object_info:
            st.error(f"Failed to get comfyui {endpoint}/object_info, please check comfyui node.")
            st.stop()
        else:
            # parse app nodes
            with st.expander("Parse comfyui node info", expanded=True):
                for node_id in api_data_json:
                    inputs = api_data_json[node_id]['inputs']
                    # check node type                   
                    class_type = api_data_json[node_id]['class_type']
                    if class_type in endpoint_object_info:
                        st.write(f":green[Check node info\, {node_id}\:{class_type}]")
                    else:
                        st.write(f":red[Node info not found\, {node_id}\:{class_type}]")
                        st.session_state['publish_invalid_node'] = True
                    
            # parse app models
            with st.expander("Parse comfyui model info", expanded=True):
                for node_id in api_data_json:
                    inputs = api_data_json[node_id]['inputs']
                    class_type = api_data_json[node_id]['class_type']
                    # check model path
                    logger.info(f"inputs, {inputs}")    
                    for key, value in inputs.items():
                        try:
                            if isinstance(value, str):
                                if is_comfyui_model_path(value):
                                    if key in endpoint_object_info[class_type]['input']['required']:
                                        model_options = endpoint_object_info[class_type]['input']['required'][key][0]
                                    elif key in endpoint_object_info[class_type]['input']['optional']:
                                        model_options = endpoint_object_info[class_type]['input']['optional'][key][0]
                                    else:
                                        model_options = []

                                    if value not in model_options:
                                        st.write(f":blue[Invalid model path\, {value}]")
                                    else:
                                        st.write(f":green[Check model path\, {value}]")
                            elif isinstance(value, dict):
                                for k, v in value.items():
                                    if is_comfyui_model_path(v):
                                        st.write(f":green[ignore path\, {k} {value}]")
                                    
                        except Exception as e:
                            st.write(f":blue[Invalid model path\, {value}]")

                                                        
        publish_button = st.button("Publish", key='publish_button', type='primary', 
                      help="Publish app to store and share with your friends")
        if publish_button:
            if st.session_state.get('publish_invalid_node', False):
                st.warning("Invalid custom node, please check custom node info.")
            else:

                # convert image to base64
                image_base64 = base64.b64encode(app.image).decode('utf-8')
                
                # call api to publish app
                do_publish_app(app.name, app.description, image_base64, app.app_conf, app.api_conf, app.workflow_conf, endpoint, app.template, AppStatus.PUBLISHED.value, cookies)
