from loguru import logger
import os
import requests
import streamlit as st
from urllib.parse import urlparse, parse_qs
from huggingface_hub import hf_hub_download
from repositories.ComfyUI.folder_paths import folder_names_and_paths, models_dir
        
@st.cache_data(ttl=24*60*60)        
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
        
@st.cache_data(ttl=3600)
def get_local_model_file(model_url):
    logger.debug(f"model_url: {model_url}")
    if model_url.startswith('https://huggingface.co'):
        try:
            # download model from huggingface model hub
            parsed_url = urlparse(model_url)
            path_parts = parsed_url.path.split('/')
            subfolder = path_parts[5:-1]
            if len(subfolder) > 0:
                subfolder = "/".join(subfolder)
                local_model_file = os.path.join(path_parts[1], path_parts[2], subfolder, path_parts[-1])
            else:
                local_model_file = os.path.join(path_parts[1], path_parts[2], path_parts[-1])
            return os.path.normpath(local_model_file)
        except Exception as e:
            logger.error(f"parse local model file from {model_url} failed, {e}")
            return None
    elif model_url.startswith('https://civitai.com'):
        try:
            # download model from civitai
            model_meta = get_civitai_model_meta(model_url)
            logger.debug(f"model_meta: {model_meta}")
            pass
        except Exception as e:
            logger.error(f"parse local model file from {model_url} failed, {e}")
            return None



def download_model(model_url, model_path):
    # parse model info from download url, 
    # eg: https://huggingface.co/segmind/SSD-1B/blob/main/unet/diffusion_pytorch_model.fp16.safetensors

    # model_url is huggingface
    if model_url.startswith('https://huggingface.co'):
        try:
            # download model from huggingface model hub
            parsed_url = urlparse(model_url)
            path_parts = parsed_url.path.split('/')
            repo_id = '/'.join(path_parts[1:3])  #
            if len(path_parts[5:-1]) > 0:
                subfolder =  "/".join(path_parts[5:-1])  # 
            else:
                subfolder = None
            
            filename = path_parts[-1]  # 最后一个元素是filename
            file_extension = filename.split('.')[-1]
            if 'ipadapter' == model_path:
                # load IPAdapterPlus
                import repositories.ComfyUI.custom_nodes.ComfyUI_IPAdapter_plus.IPAdapterPlus
            model_dir, model_extension = folder_names_and_paths[model_path]

            local_dir =  os.path.sep.join([model_dir[0], path_parts[1], path_parts[2]])
            logger.debug(f"url: {model_url} model_path: {model_path} repo_id: {repo_id}, subfolder: {subfolder}, filename: {filename} local_dir: {local_dir}")

            if not os.path.exists(local_dir):
                os.makedirs(local_dir)
            if f".{file_extension}" in model_extension:
                # save to model_dir[0]
                return hf_hub_download(repo_id=repo_id, filename=filename, subfolder=subfolder, local_dir=local_dir)
            else:
                logger.error(f"file extension {file_extension} not match {model_extension}")
                return None
        except Exception as e:
            logger.error(f"download model from {model_url} failed, {e}")
            return None 
    elif model_url.startswith('https://civitai.com'):
        try:
            # download model from civitai
            local_filename = model_url.split('/')[-1]
            # NOTE the stream=True parameter below
            with requests.get(model_url, stream=True) as r:
                r.raise_for_status()
                with open(local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192): 
                        # If you have chunk encoded response uncomment if
                        # and set chunk_size parameter to None.
                        #if chunk: 
                        f.write(chunk)
            return local_filename
            pass
        except Exception as e:
            logger.error(f"download model from {model_url} failed, {e}")
            return None
    else:
        logger.error(f"download model from {model_url} failed, not supported model url")
        return None
