import os
from loguru import logger
import threading
import subprocess
import psutil
import shutil
from modules.workspace_model import AppStatus

class CommandThread(threading.Thread):
    def __init__(self, path, command):
        super(CommandThread, self).__init__()
        self.path = path
        self.command = command
    
    def run(self):
        logger.info(f"Run command {self.command} in path {self.path}")
        result = subprocess.run(self.command, shell=True, cwd=self.path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            logger.info("Command output:", result.stdout)
        else:
            logger.warning(f"{self.command} return ", result.stderr)


def is_process_running(app_name, args):
    """
    ['/usr/local/anaconda3/bin/python', '/usr/local/anaconda3/bin/streamlit', 'run', 'comfyflow_app.py', '--server.port', '8198', '--server.address', 'localhost', '--', '--app', '11']
    """
    for process in psutil.process_iter(attrs=['pid', 'cmdline']):
        if process.info['cmdline']:
            cmdline = process.info['cmdline']
            # check all args is in cmdline
            if all(arg in cmdline for arg in args):
                logger.info(f"Process {app_name} is running, pid: {process.info['pid']}")
                return True
    return False

def kill_all_process(app_name, args):
    """
    ['/usr/local/anaconda3/bin/python', '/usr/local/anaconda3/bin/streamlit', 'run', 'comfyflow_app.py', '--server.port', '8198', '--server.address', 'localhost', '--', '--app', '11']
    """
    for process in psutil.process_iter(attrs=['pid', 'cmdline']):
        if process.info['cmdline']:
            cmdline = process.info['cmdline']
            # check all args is in cmdline
            if all(arg in cmdline for arg in args):
                logger.info(f"Kill process {app_name}, pid: {process.info['pid']}")
                process.kill()

def make_app_home(app_name):
    # remove app home first
    remove_app_home(app_name)

    app_path = os.path.join(os.getcwd(), ".apps", app_name)
    if not os.path.exists(app_path):
        os.makedirs(app_path)
        logger.info(f"make App {app_name} dir, {app_path}")

    try:
        # cp comfyflow_app.py, comfyflow.db, public, modules, .streamlit to app_path
        shutil.copyfile("./manager/comfyflow_app.py", os.path.join(app_path, "comfyflow_app.py"))
        shutil.copyfile("./comfyflow.db", os.path.join(app_path, "comfyflow.db"))
        shutil.copytree("./public", os.path.join(app_path, "public"))
        shutil.copytree("./modules", os.path.join(app_path, "modules"))
        shutil.copytree("./.streamlit", os.path.join(app_path, ".streamlit"))

        logger.info(f"App {app_name} generated, path: {app_path}")
        return app_path
    except Exception as e:
        logger.error(f"Error: {e}")
        return None

def remove_app_home(app_name):
    app_path = os.path.join(os.getcwd(), ".apps", app_name)
    if os.path.exists(app_path):
        shutil.rmtree(app_path)
        logger.info(f"App {app_name} removed, path: {app_path}")
        return True
    else:
        logger.info(f"App {app_name} does not exist, path: {app_path}")
        return False

def start_app(app_name, app_id, url):
    # url, parse server and port
    address = url.split("//")[1].split(":")[0]
    port = url.split("//")[1].split(":")[1]
    command = f"streamlit run comfyflow_app.py --server.port {port} --server.address {address} -- --app {app_id}"
    if is_process_running(app_name, ["run", "comfyflow_app.py", str(port), address]):
        logger.info(f"App {app_name} is already running, url: {url}")
        return AppStatus.RUNNING.value
    else:
        logger.info(f"start comfyflow app {app_name}")
        app_path = make_app_home(app_name)
        if app_path is None:
            logger.error(f"App {app_name} dir generated failed, path: {app_path}")
            return "failed"
        app_thread = CommandThread(app_path, command)
        app_thread.start()
        logger.info(f"App {app_name} started, url: {url}")
        return AppStatus.STARTED.value
    
def stop_app(app_name, url):
    # url, parse server and port
    address = url.split("//")[1].split(":")[0]
    port = url.split("//")[1].split(":")[1]
    if is_process_running(app_name, ["run", "comfyflow_app.py", str(port), address]):
        logger.info(f"stop comfyflow app {app_name}")
        kill_all_process(app_name, ["run", "comfyflow_app.py", str(port), address])
        remove_app_home(app_name)
        return AppStatus.STOPPING.value
    else:
        logger.info(f"App {app_name} is not running, url: {url}")
        return AppStatus.STOPPED.value

