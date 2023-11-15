
import os
import sys
from loguru import logger


def prepare_comfyui_path():
    comfyui_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'repositories', 'ComfyUI'))
    if comfyui_path not in sys.path:
        logger.info(f"add comfyui path {comfyui_path}")
        sys.path.insert(0, comfyui_path)
    return comfyui_path