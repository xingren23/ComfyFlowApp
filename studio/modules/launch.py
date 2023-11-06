
import os
import sys


def prepare_comfyui_path():
    comfyui_path = os.path.join(os.path.dirname(__file__), '..', 'repositories', 'ComfyUI')
    if comfyui_path not in sys.path:
        print(f"add comfyui path {comfyui_path}")
        sys.path.append(comfyui_path)
    return comfyui_path