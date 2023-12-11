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
def get_endpoint_object_info(endpoint):
    ret = requests.get(f"{endpoint}/object_info")
    if ret.status_code != 200:
        raise Exception(f"Failed to get comfyflow object info, {ret.content}")
    ret_json = ret.json()
    return ret_json     


def get_node_endpoint(session_cookie):
    api_url = f'{os.environ.get("COMFYFLOW_API_URL")}/api/node/list' 
    req = requests.get(api_url, cookies=session_cookie)
    if req.status_code == 200:
        logger.info(f"get node list, {req.json()}")
        return req.json()
    else:
        return None

def do_publish_app(name, description, image, app_conf, api_conf, endpoint, template, status, cookies=None):
    comfyflow_api = os.getenv('COMFYFLOW_API_URL')
    # post app to comfyflow.app
    app = {
        "name": name,
        "description": description,
        "image": image,
        "app_conf": app_conf,
        "api_conf": api_conf,
        "endpoint": endpoint,
        "template": template,
        "status": status
    }
    logger.debug(f"publish app to comfyflow.app, {app}")
    ret = requests.post(f"{comfyflow_api}/api/app/publish", json=app, cookies=cookies)
    if ret.status_code != 200:
        logger.error(f"publish app failed, {name} {ret.content}")
        return None
    else:
        logger.info(f"publish app success, {name}")
        return ret

def on_publish_workspace():
    st.session_state.pop('publish_app', None)
    logger.info("back to workspace")


def publish_app_ui(app, cookies):
    logger.info("Loading publish page")

    with page.stylable_button_container():
        header_row = row([0.85, 0.15], vertical_align="top")
        header_row.title("✈️ Publish comfyflow app")
        header_row.button("Back Workspace", help="Back to your workspace", key='publish_back_workspace', on_click=on_publish_workspace)

    with st.container():
        app_name = app.name
        api_data_json = json.loads(app.api_conf)
        app_data_json = json.loads(app.app_conf)
        
        # select endpoint
        nodes = get_node_endpoint(cookies) 
        if not nodes:
            st.info("No comfyui node found, manage your comfyui node on website: https://comfyflow.app ")
            st.stop()

        endpoint_options = [node['endpoint'] for node in nodes]
        endpoint = st.selectbox("Select endpoint", endpoint_options, key='publish_endpoint', index=0, help="Select endpoint to publish app")

        # get endpoint object info
        endpoint_object_info = get_endpoint_object_info(endpoint)
        if not endpoint_object_info:
            st.error(f"Failed to get comfyflow object info, {endpoint}")
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
            with st.expander("Parse comfyui node info", expanded=True):
                for node_id in api_data_json:
                    inputs = api_data_json[node_id]['inputs']
                    # check model path
                    for key, value in inputs.items():
                        if isinstance(value, str) and value.find('.') != -1:
                            model_type = value.split('.')[-1]
                            logger.info(f"model_type, {model_type}")
                            if f'.{model_type}' not in comfyui_supported_pt_extensions:
                                st.write(f":red[Invalid model path\, {value}]")
                                st.session_state['publish_invalid_node'] = True
                            else:
                                st.write(f":green[Check model path\, {value}]")

        # # config app models
        # with st.expander("Config app models", expanded=True):
        #     if 'object_model' in st.session_state:
        #         object_model = st.session_state['object_model']
        #         for node_id in api_data_json:
        #             inputs = api_data_json[node_id]['inputs']
        #             class_type = api_data_json[node_id]['class_type']
        #             if class_type in object_model:
        #                 model_name_path = object_model[class_type]
        #                 input_model_row = row([0.5, 0.5])
        #                 for param in inputs:
        #                     if param in model_name_path:
        #                         model_input_name = f"{node_id}:{class_type}:{inputs[param]}"
        #                         input_model_row.text_input("App model name", value=model_input_name, help="App model name")
        #                         input_model_row.text_input("Input model url", key=model_input_name, help="Input model url of huggingface model hub")
        #     else:
        #         st.error(f"{st.session_state['get_comfyflow_model_info_error']}")
        #         st.stop()
                                                        
        publish_button = st.button("Publish", key='publish_button', type='primary', 
                      help="Publish app to store and share with your friends")
        if publish_button:
            if 'publish_invalid_node' in st.session_state:
                st.warning("Invalid node, please check node info.")
            else:
                # # check model url
                # model_size = 0
                # models = {}
                # for node_id in api_data_json:
                #     inputs = api_data_json[node_id]['inputs']
                #     class_type = api_data_json[node_id]['class_type']
                #     if class_type in object_model:
                #         model_node_inputs = {}
                #         model_name_path = object_model[class_type]
                #         for param in inputs:
                #             if param in model_name_path:
                #                 model_path = model_name_path[param]
                #                 model_input_name = f"{node_id}:{class_type}:{inputs[param]}"
                #                 if not st.session_state[model_input_name]:
                #                     st.warning(f"Please input model url for {model_input_name}")
                #                     st.stop()
                #                 else:
                #                     model_url = st.session_state[model_input_name]
                #                     model_meta = get_model_meta(model_url)
                #                     if model_meta:
                #                         model_node_inputs[param] = {
                #                             "url": model_meta['model_url'],
                #                             "size": model_meta['size'],
                #                             "path": model_path,
                #                         }
                #                     else:
                #                         st.warning(f"Invalid model url for {model_input_name}")
                #                         st.stop()
                #         if model_node_inputs:
                #             models[node_id] = {"inputs": model_node_inputs}
                    
                # # update app_conf and status
                # app_data_json['models'] = models
                # app_data = json.dumps(app_data_json)
                # logger.info(f"update models, {app_data}")
                # get_workspace_model().update_app_publish(app_name, app_data)

                # convert image to base64
                image_base64 = base64.b64encode(app.image).decode('utf-8')

                # call api to publish app
                ret = do_publish_app(app.name, app.description, image_base64, app.app_conf, app.api_conf, endpoint, app.template, AppStatus.PUBLISHED.value, cookies)
                if ret:
                    st.success("Publish success, you can share this app with your friends.")
                else:
                    st.error("Publish app error")
