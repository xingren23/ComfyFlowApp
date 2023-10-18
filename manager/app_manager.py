from loguru import logger
import threading
import subprocess
import psutil

class CommandThread(threading.Thread):
    def __init__(self, path, command):
        super(CommandThread, self).__init__()
        self.path = path
        self.command = command
    
    def run(self):
        cmd = f"cd {self.path} ; {self.command}"
        logger.info(f"Run command {cmd}")
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            logger.info("Command output:", result.stdout)
        else:
            logger.error("Error:", result.stderr)

def is_process_running(app_name, args):
    """
    ['/usr/local/anaconda3/bin/python', '/usr/local/anaconda3/bin/streamlit', 'run', 'comfyflow_app.py', '--server.port', '8198', '--server.address', 'localhost', '--', '--app', 'rembg']
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
    ['/usr/local/anaconda3/bin/python', '/usr/local/anaconda3/bin/streamlit', 'run', 'comfyflow_app.py', '--server.port', '8198', '--server.address', 'localhost', '--', '--app', 'rembg']
    """
    for process in psutil.process_iter(attrs=['pid', 'cmdline']):
        if process.info['cmdline']:
            cmdline = process.info['cmdline']
            # check all args is in cmdline
            if all(arg in cmdline for arg in args):
                logger.info(f"Kill process {app_name}, pid: {process.info['pid']}")
                process.kill()


def start_app(app_name, url):
    # url : http://localhost:8188, parse server and port
    address = url.split("//")[1].split(":")[0]
    port = url.split("//")[1].split(":")[1]
    command = f"streamlit run comfyflow_app.py --server.port {port} --server.address {address} -- --app {app_name}"
    if is_process_running(app_name, ["run", "comfyflow_app.py", str(port), address, app_name]):
        logger.info(f"App {app_name} is already running, url: {url}")
        return "running"
    else:
        logger.info(f"start comfyflow app {app_name}")
        app_thread = CommandThread("manager", command)
        app_thread.start()
        logger.info(f"App {app_name} started, url: {url}")
        return "started"
    
def stop_app(app_name, url):
    # url : http://localhost:8188, parse server and port
    address = url.split("//")[1].split(":")[0]
    port = url.split("//")[1].split(":")[1]
    if is_process_running(app_name, ["run", "comfyflow_app.py", str(port), address, app_name]):
        logger.info(f"stop comfyflow app {app_name}")
        kill_all_process(app_name, ["run", "comfyflow_app.py", str(port), address, app_name])
        return "stopping"
    else:
        logger.info(f"App {app_name} is not running, url: {url}")
        return "stopped"

