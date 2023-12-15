from loguru import logger
import os
import requests
import streamlit as st
from modules.page import page_init
from modules import get_comfyflow_token
from streamlit_extras.row import row
from modules.page import stylable_button_container
import base64
from modules.comfyflow import Comfyflow
from modules import get_inner_comfy_client, check_inner_comfyui_alive


# def bytes_to_human_readable(size_in_bytes, decimal_places=2):
#     for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
#         if size_in_bytes < 1024.0:
#             break
#         size_in_bytes /= 1024.0
#     return f"{size_in_bytes:.{decimal_places}f} {unit}"

# class ProgressEventState():
#     RUNNING = "running"
#     COMPLETE = "complete"
#     ERROR = "error"
#     def __init__(self, app_id, info, state) -> None:
#         self.app_id = app_id
#         self.info = info
#         self.state = state

#     def __str__(self) -> str:
#         return f"ProgressEventState: app_id: {self.app_id}, info: {self.info}, state: {self.state}"

# class InstallThread(Thread): 
#     def __init__(self, app, queue):
#         super(InstallThread, self).__init__()
#         self.app_id = app.id
#         self.app_name = app.name
#         self.app_conf_json = json.loads(app.app_conf)
#         self.api_conf_json = json.loads(app.api_conf)
#         logger.debug(f"Install app {self.app_name} with app_conf {self.app_conf_json} and api_conf {self.api_conf_json}")
#         self.queue = queue


#     def dispatch_event(self, event):            
#         if self.queue is not None:
#             logger.debug(f"Dispatch event, {event}")
#             self.queue.put(event)
#         else:
#             logger.info("queue is none")

#     def run(self):    
#         from modules.download import download_model, get_local_model_file
#         try:
#             models_size = 0
#             models = []
#             if 'models' in self.app_conf_json:
#                 node_models = self.app_conf_json['models']
#                 for node_id in node_models:
#                     inputs = node_models[node_id]['inputs']
#                     for param in inputs:
#                         model_info = inputs[param]
#                         models_size += model_info['size']
#                         models.append(model_info)
#             status_info = f"App {self.app_name} started to download {len(models)} models, total size {bytes_to_human_readable(models_size)}"
#             status_event = ProgressEventState(self.app_id, status_info, ProgressEventState.RUNNING)
#             self.dispatch_event(status_event)

#             # download 
#             download_size = 0
#             for model in models:
#                 model_url = model['url']
#                 model_path = model['path']
#                 ret = download_model(model_url=model_url, model_path=model_path)
#                 if ret is None:
#                     status_info = f":red[download model from {model_url} to {model_path} failed]"
#                     status_event = ProgressEventState(self.app_id, status_info, ProgressEventState.ERROR)
#                     self.dispatch_event(status_event)
#                     return
#                 else:
#                     download_size += model['size']
#                     status_info = f"download model from {model_url} to {model_path}, size {bytes_to_human_readable(model['size'])}, percent {download_size / models_size * 100:.2f}%"
#                     status_event = ProgressEventState(self.app_id, status_info, ProgressEventState.RUNNING)
#                     self.dispatch_event(status_event)

#             status_info = f"App {self.app_name} download finished"
#             status_event = ProgressEventState(self.app_id, status_info, ProgressEventState.RUNNING)
#             self.dispatch_event(status_event)

#             # install, update api_conf
#             if 'models' in self.app_conf_json:
#                 node_models = self.app_conf_json['models']
#                 for node_id in node_models:
#                     inputs = node_models[node_id]['inputs']
#                     for param in inputs:
#                         model_info = inputs[param]
#                         local_model_file = get_local_model_file(model_info['url'])
#                         if local_model_file is not None:
#                             self.api_conf_json[node_id]['inputs'][param] = local_model_file
#                             logger.debug(f"update api_conf_json: {node_id} {param} {local_model_file}")
#                         else:
#                             status_info = f"parse local model file from {model_info['url']} failed"
#                             status_event = ProgressEventState(self.app_id, status_info, ProgressEventState.ERROR)
#                             self.dispatch_event(status_event)
#                             return 

#                 logger.debug(f"api_conf_json: {self.api_conf_json}")
#                 get_myapp_model().update_api_conf(self.app_id, json.dumps(self.api_conf_json))

#             status_info = f"App {self.app_name} install success"
#             status_event = ProgressEventState(self.app_id, status_info, ProgressEventState.COMPLETE)
#             self.dispatch_event(status_event)
#             logger.info(f"App {self.app_name} installed")
#         except Exception as e:
#             logger.error(f"Install app error, {e}")
#             status_info = f"App {self.app_name} install error, {e}"
#             status_event = ProgressEventState(self.app_id, status_info, ProgressEventState.ERROR)
#             self.dispatch_event(status_event)

# def install_app(app):
#     if 'authentication_status' not in st.session_state or not st.session_state['authentication_status']:
#         logger.warning("Please go to homepage for your login :point_left:")
#         return
    
#     # get app details
#     app_detail = get_app_details(app.id)
#     if app_detail is None:
#         logger.error(f"Get app {app.name} details failed")
#         st.error(f"Get app {app.name} details failed")
#         return
#     else:
#         get_myapp_model().update_app_conf(app.id, app_detail['app_conf'])
#         get_myapp_model().update_api_conf(app.id, app_detail['api_conf'])
#         st.session_state['install_app'] = True
        
# def update_install_progress(app, status_queue):
#     if 'authentication_status' not in st.session_state or not st.session_state['authentication_status']:
#         st.warning("Please go to homepage for your login :point_left:")
#         return
    
#     get_myapp_model().update_app_status(app.id, AppStatus.INSTALLING.value)
#     if 'install_app' not in st.session_state:
#         logger.error(f"Install app {app.name} failed, please try again")
#         return
    
#     logger.info(f"Start install thread for {app.name} ...")
#     app_detail = get_myapp_model().get_app_by_id(app.id)
#     install_thread = InstallThread(app_detail, status_queue)
#     add_script_run_ctx(install_thread)
#     install_thread.start()

#     with st.status(f"Waiting for install {app.name} ...", state="running", expanded=True) as install_progress:
#         while True:
#             try:
#                 status_event = status_queue.get()
#                 logger.debug(f"Got install status event {status_event}")
#                 info = status_event.info
#                 state = status_event.state
#                 if state == ProgressEventState.RUNNING:
#                     install_progress.write(info)
#                 elif state == ProgressEventState.COMPLETE:
#                     install_progress.write(info)
#                     install_progress.update(label=f"Install app {app.name} success", state="complete", expanded=True)
#                     get_myapp_model().update_app_status(app.id, AppStatus.INSTALLED.value)
#                     break
#                 elif state == ProgressEventState.ERROR:
#                     install_progress.write(info)
#                     install_progress.update(label=f"Install app {app.name} error", state="error", expanded=True)
#                     get_myapp_model().update_app_status(app.id, AppStatus.ERROR.value)
#                     break
#             except Exception as e:
#                 logger.warning(f"Queue get error {e}")
#                 continue
        
#     install_thread.join()
#     logger.info(f"Install thread for {app.name} finished")
#     st.session_state.pop('install_app', None)

def is_invalid_email(email):
    if email is None or len(email) == 0 or '@' not in email:
        return True
    return False

def click_enter_app(app):
    app_details = get_app_details(app['id'])
    st.session_state["try_enter_app"] = app_details

def click_join_app(app):
    join_key = f"join_app_{app['id']}"
    if join_key not in st.session_state:
        st.session_state[join_key] = app
    else:
        st.session_state.pop(join_key, None)

def submit_join_app(app):
    email = st.session_state[f"join_email_{app['id']}"]
    if is_invalid_email(email):
        logger.warning(f"Invalid email {email}")
        st.error("Your email is invalid")
        return None
    if cookies is None:
        st.error("Please go to homepage for your login :point_left:")
        return None
 
    comfyflow_api = os.getenv('COMFYFLOW_API_URL')
    ret = requests.post(f"{comfyflow_api}/api/app/waiting/join", json={'email': email, 'app_id': app['id']}, cookies=cookies)
    if ret.status_code == 200:
        st.success(f"Join waiting list for app {app['name']} success")
        return ret.json()
    else:
        st.error(f"Join waiting list for app {app['name']} failed, {ret.text}")
        return None
    
@st.cache_data(ttl=60)
def get_app_waiting_list():
    comfyflow_api = os.getenv('COMFYFLOW_API_URL')
    ret = requests.get(f"{comfyflow_api}/api/app/waiting/list", cookies=cookies)
    if ret.status_code == 200:
        return ret.json()
    else:
        logger.error(f"Get app waiting list failed, {ret.text}")
        return []


def  get_actived_endpoint(app):
    if 'active_endpoints' in st.session_state:
        active_nodes = st.session_state['active_endpoints']
        endpoint = app.get('endpoint', '')
        if endpoint in active_nodes:
            return endpoint
    return None

def create_app_info_ui(app): 
    app_row = row([1, 3.6, 1.2, 3, 1.2], vertical_align="bottom")
    try:
        if 'image' in app:
            app_row.image(base64.b64decode(app['image']))
        else:
            app_row.image("public/images/app-150.png")
    except Exception as e:
        logger.error(f"load app image error, {e}")

    # get description limit to 200 chars
    description = app['description']
    if len(description) > 160:
        description = description[:160] + "..."                
    app_row.markdown(f"""
                    #### {app['name']}
                    {description}
                    """)
    app_row.markdown(f"""
                    #### Author
                    {app['username']}
                    """)
    # Enter app for vip member
    endpoint = get_actived_endpoint(app)
    if endpoint:
        app_row.markdown(f"""
                     #### Endpoint
                    {endpoint}
                    """)
            
        try_enter_button = app_row.button("Enter", type='primary', help="Enter to use app", key=f"try_enter_{app['id']}",
                                      on_click=click_enter_app, args=(app,))
        if try_enter_button:
            logger.info(f"try enter app {app['name']}")
    else:
        app_row.markdown("""
                    #### Endpoint
                    https://xxxxxxxx.comfyflow.app
                    """)
        join_key = f"join_app_{app['id']}"
        join_label = app['waiting'] and "Joined" or "Join"
        join_help = app['waiting'] and "You have joined waiting list" or "Join waiting list to use app online"
        app_row.button(join_label, type="primary", help=join_help, key=f"join_{app['id']}", on_click=click_join_app, args=(app,))
        if join_key in st.session_state:
            join_row = row([0.6, 0.4], vertical_align="bottom")
            join_row.text_input("Email", key=f"join_email_{app['id']}", value=app['waiting_email'], placeholder="Please input your email")
            join_waiting_button = join_row.button("Join waiting list", type='primary', help="Join waiting list to use app online", key=f"join_waiting_{app['id']}")
            if join_waiting_button:
                ret = submit_join_app(app)
                if ret is not None:
                    st.session_state.pop(join_key, None)
        

@st.cache_data(ttl=60)
def fetch_app_info():
    # get apps from comfyflow.app
    comfyflow_api = os.getenv('COMFYFLOW_API_URL')
    logger.debug(f"get all app from {comfyflow_api}")
    ret = requests.get(f"{comfyflow_api}/api/app/all", cookies=cookies)
    if ret.status_code != 200:
        st.error(f"Refresh apps from {comfyflow_api} failed, {ret.text}")
    else:
        logger.info(f"fetch apps app, get {len(ret.json())} app success")
        return ret.json()

@st.cache_data(ttl=60*60)    
def get_app_details(app_id):
    comfyflow_api = os.getenv('COMFYFLOW_API_URL')
    logger.debug(f"get app {app_id} details from {comfyflow_api}")
    ret = requests.get(f"{comfyflow_api}/api/app/{app_id}", cookies=cookies)
    if ret.status_code != 200:
        st.error(f"Get app {app_id} details from {comfyflow_api} failed, {ret.text}")
    else:
        comfyflow_app = ret.json()
        return comfyflow_app

@st.cache_data(ttl=60)
def get_active_nodes(session_cookie):
    api_url = f'{os.environ.get("COMFYFLOW_API_URL")}/api/node/actives' 
    req = requests.get(api_url, cookies=session_cookie)
    if req.status_code == 200:
        logger.debug(f"get active node list, {req.json()}")
        return req.json()
    else:
        return None

def on_back_store():
    st.session_state.pop('try_enter_app', None)
    logger.info("back to app store")


def try_enter_app_ui(app):
    with st.container():
        name = app['name']
        description = app['description']
        status = app['status']
        logger.info(f"try app {name}, status: {status}")

        with stylable_button_container():
            header_row = row([0.85, 0.15], vertical_align="top")
            header_row.title(f"{name}")
            header_row.button("App Store", help="Back to app store", key='try_back_store', on_click=on_back_store)

        st.markdown(f"{description}")
        api_data = app['api_conf']
        app_data = app['app_conf']
        endpoint = app['endpoint']
        comfy_client = get_inner_comfy_client(endpoint)
        comfyflow = Comfyflow(comfy_client=comfy_client, api_data=api_data, app_data=app_data)
        comfyflow.create_ui(show_header=False)  

page_init()

with st.container():
    if 'token_cookie' not in st.session_state:
        comfyflow_token = get_comfyflow_token()
        if comfyflow_token is not None:
            cookies = {'comfyflow_token': comfyflow_token}
            st.session_state['token_cookie'] = cookies
        else:
            cookies = None
    else:
        cookies = st.session_state['token_cookie']
    
    if 'try_enter_app' in st.session_state:
        app = st.session_state['try_enter_app']
        # start comfyui
        if not check_inner_comfyui_alive(app['endpoint']):
            st.error(f"Start app failed, {app['name']}")
        else:
            logger.info(f"Start app ..., {app['name']}")
            try_enter_app_ui(app)
    else:
        header_row = row([0.85, 0.15], vertical_align="bottom")
        header_row.markdown("""
                ### App Store
                This is a simple app store, you could explore apps here.
                """)

        if cookies is None:
            active_endpoints = []
        else:
            active_nodes = get_active_nodes(cookies)
            active_endpoints = [node['endpoint'] for node in active_nodes]
        st.session_state['active_endpoints'] = active_endpoints

        app_waiting_list = get_app_waiting_list()
        app_waitings = {app['app_id']: app for app in app_waiting_list}
        apps = fetch_app_info()
        for app in apps:
            st.divider()
            
            if app['id'] in app_waitings:
                app['waiting'] = True
                app['waiting_email'] = app_waitings[app['id']]['email']
            else:
                app['waiting'] = False
                app['waiting_email'] = None
            create_app_info_ui(app)

    