from loguru import logger
import os
import requests
from urllib.parse import urlparse
from huggingface_hub import hf_hub_download
from repositories.ComfyUI.folder_paths import folder_names_and_paths

def get_local_model_file(model_url):
    if 'huggingface' in model_url:
        try:
            # download model from huggingface model hub
            parsed_url = urlparse(model_url)
            path_parts = parsed_url.path.split('/')
            subfolder = path_parts[5:-1]
            if len(subfolder) > 0:
                subfolder = os.path.sep.join(subfolder)
                local_model_file = os.path.join(path_parts[1], path_parts[2], subfolder, path_parts[-1])
            else:
                local_model_file = os.path.join(path_parts[1], path_parts[2], path_parts[-1])
            return os.path.normpath(local_model_file)
        except Exception as e:
            logger.error(f"parse local model file from {model_url} failed, {e}")
            return None

def download_model(model_url, model_path):
    # parse model info from download url, 
    # eg: https://huggingface.co/segmind/SSD-1B/blob/main/unet/diffusion_pytorch_model.fp16.safetensors

    # model_url is huggingface
    if 'huggingface' in model_url:
        try:
            # download model from huggingface model hub
            parsed_url = urlparse(model_url)
            path_sep = '/'
            path_parts = parsed_url.path.split('/')
            repo_id = path_sep.join(path_parts[1:3])  #
            if len(path_parts[5:-1]) > 0:
                subfolder = path_sep.join(path_parts[5:-1])  # 
            else:
                subfolder = None
            filename = path_parts[-1]  # 最后一个元素是filename
            file_extension = filename.split('.')[-1]
            model_dir, model_extension = folder_names_and_paths[model_path]
            local_dir = path_sep.join([model_dir[0], repo_id])
            logger.debug(f"repo_id: {repo_id}, subfolder: {subfolder}, filename: {filename} local_dir: {local_dir}")  
            if f".{file_extension}" in model_extension:
                # save to model_dir[0]
                return hf_hub_download(repo_id=repo_id, filename=filename, subfolder=subfolder, local_dir=local_dir)
            else:
                logger.error(f"file extension {file_extension} not match {model_extension}")
                return None
        except Exception as e:
            logger.error(f"download model from {model_url} failed, {e}")
            return None