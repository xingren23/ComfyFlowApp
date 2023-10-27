import json
import uuid
import requests
import websocket
from PIL import Image
import io
import threading
from loguru import logger


class ComfyClient:
    def __init__(self, server_addr) -> None:
        self.client_id = str(uuid.uuid4())
        self.server_addr = server_addr
        logger.info(f"Comfy client id: {self.client_id}")

    def get_node_class(self):
        object_info_url = f"http://{self.server_addr}/object_info"
        logger.info(f"Got object info from {object_info_url}")
        resp = requests.get(object_info_url, timeout=3)
        if resp.status_code != 200:
            raise Exception(f"Failed to get object info from {object_info_url}")
        return resp.json()
    
    def queue_remaining(self):
        """
        return: 
        "exec_info": {
            "queue_remaining": 0
        }
        """
        url = f"http://{self.server_addr}/prompt"
        logger.info(f"Got remaining from {url}")
        resp = requests.get(url)
        if resp.status_code != 200:
            raise Exception(f"Failed to get queue from {url}")
        return resp.json()['exec_info']['queue_remaining']
    
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
    
    
    def gen_images(self, prompt, queue):
        logger.info(f"Generating images from comfyui, {prompt}")
        thread = threading.Thread(target=self._websocket_loop, args=(prompt, queue))
        thread.start()

        # queue prompt 
        prompt_id = self.queue_prompt(prompt)['prompt_id']  
        logger.info(f"Send prompt to comfyui, {prompt_id}")
        
        return prompt_id

    def _websocket_loop(self, prompt, queue):
        logger.info(f"Connecting to websocket server, {self.server_addr}")
        ws = websocket.WebSocket()
        ws.connect("ws://{}/ws?clientId={}".format(self.server_addr, self.client_id))

        def dispatch_event(queue, event):            
            if queue is not None:
                event_type = event['type']
                if event_type == 'b_preview':
                    logger.debug(f"Dispatch event, {event_type}")
                else:
                    logger.debug(f"Dispatch event, {event}")
                queue.put(event)
            else:
                logger.info("queue is none")

        while True:
            out = ws.recv()
            try:
                if isinstance(out, str):
                    msg = json.loads(out)
                    msg_type = msg['type']
                    logger.debug(f"Got message from websocket server, {msg_type}, {msg}")
                    if msg_type == "status":
                        if "sid" in msg.get("data"):
                            self.client_id = msg["data"]["sid"]
                            # Set window.name to self.client_id
                        status_data = msg["data"]["status"]
                        # Dispatch status event with status_data
                        dispatch_event(queue, {"type": "status", "data": status_data})
                    elif msg_type == "progress":
                        # Dispatch progress event with msg["data"]
                        dispatch_event(queue, {"type": "progress", "data": msg["data"]})
                    elif msg_type == "executing":
                        # Dispatch executing event with msg["data"]["node"]
                        dispatch_event(queue, {"type": "executing", "data": msg["data"]["node"]})
                        if msg["data"]["node"] is None:
                            logger.info("worflow finished, exiting websocket loop")
                            break
                    elif msg_type == "executed":
                        # Dispatch executed event with msg["data"]
                        dispatch_event(queue, {"type": "executed", "data": msg["data"]})
                    elif msg_type == "execution_start":
                        # Dispatch execution_start event with msg["data"]
                        dispatch_event(queue, {"type": "execution_start", "data": msg["data"]})
                    elif msg_type == "execution_error":
                        # Dispatch execution_error event with msg["data"]
                        dispatch_event(queue, {"type": "execution_error", "data": msg["data"]})
                    elif msg_type == "execution_cached":
                        # Dispatch execution_cached event with msg["data"]
                        dispatch_event(queue, {"type": "execution_cached", "data": msg["data"]})
                    else:
                        logger.warning(f"Unknown message type {msg_type}")
                    
                elif isinstance(out, bytes):
                    view = memoryview(out)
                    event_type = int.from_bytes(view[:4], 'big')
                    buffer = view[4:]
                    if event_type == 1:
                        view2 = memoryview(buffer)
                        image_type = int.from_bytes(view2[:4], 'big')
                        image_mime = ""
                        if image_type == 1:
                            image_mime = "image/jpeg"
                        elif image_type == 2:
                            image_mime = "image/png"
                        
                        image_blob = buffer[4:]
                        logger.debug(f"Got binary websocket message of type {event_type}, {image_mime}, {len(image_blob)}")
                        # Dispatch b_preview event with image_blob
                        image = Image.open(io.BytesIO(image_blob))
                        dispatch_event(queue, {"type": "b_preview", "data": image})
                    else:
                        logger.warning(f"Unknown binary websocket message of type {event_type}")      

            except Exception as e:
                logger.error(f"Error while processing websocket message, {e}")
                raise e
