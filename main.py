import os
import argparse
import requests
from loguru import logger

from comfyflowapp import ComfyFlowApp
 

NODE_CLASS_MAPPINGS = {}

def register_node_class(server_addr):
    object_info_url = f"http://{server_addr}/object_info"
    logger.info(f"Got object info from {object_info_url}")
    resp = requests.get(object_info_url, timeout=3)
    if resp.status_code != 200:
        raise Exception(f"Failed to get object info from {object_info_url}")
    object_info = resp.json()
    
    return object_info


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--server_addr", type=str, default="127.0.0.1:8188")
    parser.add_argument("--workflow", type=str, default="default")
    try:
        args = parser.parse_args()
        server_addr = args.server_addr
        workflow = args.workflow

        api_file = f"conf/workflows/{workflow}/api.json"
        app_file = f"conf/workflows/{workflow}/app.json"

        if not os.path.exists(api_file) or not os.path.exists(app_file):
            raise Exception(f"Invalid workflow {workflow}, api file {api_file} or app file {app_file} does not exist")

        logger.info("Starting ComfyFlowApp")

        NODE_CLASS_MAPPINGS = register_node_class(server_addr)
        app = ComfyFlowApp(server_addr=server_addr, api_file=api_file, app_file=app_file)
    except SystemExit as e:
        logger.error(e)
        exit()

    