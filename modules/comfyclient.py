import json
import uuid
import requests
import websocket
from loguru import logger


class ComfyClient:
    def __init__(self, server_addr) -> None:
        self.client_id = str(uuid.uuid4())
        self.server_addr = server_addr

    def get_node_class(self):
        object_info_url = f"http://{self.server_addr}/object_info"
        logger.info(f"Got object info from {object_info_url}")
        resp = requests.get(object_info_url, timeout=3)
        if resp.status_code != 200:
            raise Exception(f"Failed to get object info from {object_info_url}")
        return resp.json()
    
    
    def queue_prompt(self, prompt):
        p = {"prompt": prompt, "client_id": self.client_id}
        data = json.dumps(p).encode('utf-8')
        logger.info(f"Sending prompt to server, {self.client_id}")
        resp = requests.post(f"http://{self.server_addr}/prompt", data=data)
        if resp.status_code != 200:
            raise Exception(f"Failed to send prompt to server, {resp.status_code}")
        return resp.json()

    def get_image(self, filename, subfolder, folder_type):
        url = f"http://{self.server_addr}/view?filename={filename}&subfolder={subfolder}&type={folder_type}"
        logger.info(f"Getting image from server, {url}")
        resp = requests.get(url)
        if resp.status_code != 200:
            raise Exception(f"Failed to get image from server, {resp.status_code}")
        return resp.content

    def upload_image(self, imagefile, subfolder, type, overwrite):
        data = {"subfolder": subfolder, "type": type, "overwrite": overwrite}
        logger.info(f"Uploading image to server, {data}")
        resp = requests.post(f"http://{self.server_addr}/upload/image", data=data, files=imagefile)
        if resp.status_code != 200:
            raise Exception(f"Failed to upload image to server, {resp.status_code}")
        return resp.json()

    def get_history(self, prompt_id):
        logger.info(f"Getting history from server, {prompt_id}")
        resp = requests.get(f"http://{self.server_addr}/history/{prompt_id}")
        if resp.status_code != 200:
            raise Exception(f"Failed to get history from server, {resp.status_code}")
        return resp.json()

    def gen_images(self, prompt):
        ws = websocket.WebSocket()
        logger.info(f"Connecting to websocket server, {self.server_addr}")
        ws.connect("ws://{}/ws?clientId={}".format(self.server_addr, self.client_id))

        prompt_id = self.queue_prompt(prompt)['prompt_id']  
        output_images = {}
        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'executing':
                    data = message['data']
                    if data['node'] is None and data['prompt_id'] == prompt_id:
                        logger.info(f"Execution is done, {prompt_id}")
                        break #Execution is done
            else:
                continue #previews are binary data

        history = self.get_history(prompt_id)[prompt_id]
        for node_id in history['outputs']:
            node_output = history['outputs'][node_id]
            if 'images' in node_output:
                images_output = []
                for image in node_output['images']:
                    image_data = self.get_image(image['filename'], image['subfolder'], image['type'])
                    images_output.append(image_data)
                if len(images_output) > 0:
                    output_images[node_id] = images_output
                    logger.info(f"Got images from server, {node_id}, {len(images_output)}")

        logger.info(f"Gen images from server, {len(output_images)}, {output_images.keys()}")
        return output_images