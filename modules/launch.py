import os
import sys
import urllib.parse as urlparse
from loguru import logger
import streamlit as st
import subprocess
from threading import Thread
from modules import check_inner_comfyui_alive
from streamlit.runtime.scriptrunner import add_script_run_ctx


def prepare_comfyui_path():
    comfyui_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'repositories', 'ComfyUI'))
    if comfyui_path not in sys.path:
        logger.info(f"add comfyui path {comfyui_path}")
        sys.path.insert(0, comfyui_path)
    return comfyui_path

class ComfyUIThread(Thread):
    def __init__(self, server_addr, path):
        Thread.__init__(self)
        self.server_addr = server_addr
        self.path = path

    def run(self):
        try:
            import sys
            server_port = urlparse.urlparse(self.server_addr).netloc
            address, port = server_port.split(":")
            # start local comfyui
            if address == "localhost" or address == "127.0.0.1":
                command = f"{sys.executable} main.py --port {port} --disable-auto-launch"
                logger.info(f"start inner comfyui, {command} path {self.path}, sys.path {sys.path}")
                comfyui_log = open('comfyui.log', 'w')
                subprocess.run(command, cwd=self.path, shell=True,
                               stdout=comfyui_log, stderr=comfyui_log, text=True)
                comfyui_log.close()
                return True
            else:
                # start remote comfyui
                st.error(f"could not start remote comfyui, {address}")
                return False
        except Exception as e:
            logger.error(f"running comfyui error, {e}")


def start_comfyui():
    try:
        if check_inner_comfyui_alive():
            logger.info("inner comfyui is alive")
            return True

        logger.info("start inner comfyui ...")

        comfyui_path = prepare_comfyui_path()
        server_addr = os.getenv('INNER_COMFYUI_SERVER_ADDR')
        comfyui_thread = ComfyUIThread(server_addr, comfyui_path)
        add_script_run_ctx(comfyui_thread)
        comfyui_thread.start()
        # wait 2 seconds for comfyui start
        comfyui_thread.join(5)
        if comfyui_thread.is_alive():
            logger.info("start inner comfyui success")
            return True
        else:
            logger.error("start inner comfyui timeout")
            return False
    except Exception as e:
        logger.error(f"start inner comfyui error, {e}")