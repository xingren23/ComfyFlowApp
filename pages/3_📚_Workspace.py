import os
import requests
from io import BytesIO
from loguru import logger
import streamlit as st
import modules.page as page
from modules import get_workspace_model, check_comfyui_alive, get_comfyflow_token
from streamlit_extras.row import row
from manager.app_manager import start_app, stop_app
from modules.workspace_model import AppStatus
from streamlit import config
from modules.new_app import new_app_ui, edit_app_ui
from modules.preview_app import preview_app_ui
from modules.publish_app import publish_app_ui
import random


def create_app_info_ui(app):
    app_row = row([1, 4.6, 1.2, 2, 1.2], vertical_align="bottom")
    try:
        if app.image is not None:
            
            app_row.image(BytesIO(app.image))
        else:
            app_row.image("./public/images/app-150.png")
    except Exception as e:
        logger.error(f"load app image error, {e}")

    # get description limit to 200 chars
    description = app.description
    if len(description) > 160:
        description = description[:160] + "..."                
    app_row.markdown(f"""
                    #### {app.name}
                    {description}
                    """)
    app_author = app.username
    app_row.markdown(f"""
                    #### Author
                    {app_author}
                    """)
    app_row.markdown(f"""
                    #### Web Site
                    🌐 {app.url}
                    """)
    app_row.markdown(f"""
                    #### Status
                    {app.status}
                    """)

@st.cache_data(ttl=60*60)
def get_comfyflow_object_info(cookies):
    comfyflow_api = os.getenv('COMFYFLOW_API_URL')
    # request comfyflow object info
    object_info = requests.get(f"{comfyflow_api}/api/comfyflow/object_info", cookies=cookies)
    if object_info.status_code != 200:
        logger.error(f"Get comfyflow object info failed, {object_info.text} {cookies}")
        st.session_state['get_comfyflow_object_info_error'] = f"Get comfyflow object info failed, {object_info.text}"
        return None
    logger.info(f"get_comfyflow_object_info, {object_info}")
    return object_info.json()

@st.cache_data(ttl=60*60)
def get_comfyflow_model_info(cookies):
    comfyflow_api = os.getenv('COMFYFLOW_API_URL')
    # request comfyflow object info
    model_info = requests.get(f"{comfyflow_api}/api/comfyflow/model_info", cookies=cookies)
    if model_info.status_code != 200:
        logger.error(f"Get comfyflow model info failed, {model_info.text}")
        st.session_state['get_comfyflow_model_info_error'] = f"Get comfyflow model info failed, {model_info.text}"
        return None
    logger.info(f"get_comfyflow_model_info, {model_info}")
    return model_info.json()     


def click_new_app():
    logger.info("new app...")
    st.session_state['new_app'] = True    
    st.session_state.pop('edit_app', None)
    st.session_state.pop('preview_app', None)
    st.session_state.pop('publish_app', None)

def click_edit_app(app):
    logger.info(f"edit app: {app.name}")
    st.session_state['edit_app'] = app
    st.session_state.pop('new_app', None)
    st.session_state.pop('preview_app', None)
    st.session_state.pop('publish_app', None)

def click_preview_app(app):    
    logger.info(f"preview app: {app.name}")
    st.session_state['preview_app'] = app
    st.session_state.pop('new_app', None)
    st.session_state.pop('edit_app', None)
    st.session_state.pop('publish_app', None)


def click_publish_app(app):
    if app.status == AppStatus.CREATED.value:
        logger.warning(f"Please preview the app {app.name} first")
        return
    
    if 'token_cookie' in st.session_state:
        object_info = get_comfyflow_object_info(cookies)
        if object_info is None:
            return
        else:
            st.session_state['object_info'] = object_info
            
        object_model = get_comfyflow_model_info(cookies)
        if object_model is None:
            return
        else:
            st.session_state['object_model'] = object_model
    else:
        return 

    logger.info(f"publish app: {app.name} status: {app.status}")
    st.session_state['publish_app'] = app
    st.session_state.pop('new_app', None)
    st.session_state.pop('preview_app', None)
    

def click_delete_app(name):
    logger.info(f"delete app: {name}")
    get_workspace_model().delete_app(name)

def click_install_app(app):
    if app.status == AppStatus.CREATED.value:
        logger.warning(f"Please preview the app {app.name} first")
        return
    
    get_workspace_model().update_app_install(app.name)
    logger.info(f"install App {app.name} success")
    st.session_state['app_install_ret'] = AppStatus.INSTALLED.value

def ready_start_app(status):
    if status == AppStatus.PREVIEWED.value or status == AppStatus.PUBLISHED.value or status == AppStatus.INSTALLED.value:
        return True
    else:
        return False
    
def click_start_app(name, id, status):
    logger.info(f"start app: {name} status: {status}")
    if ready_start_app(status):
        if not check_comfyui_alive():
            logger.error("ComfyUI server is not alive, please check it")
            st.session_state['app_start_ret'] = AppStatus.ERROR.value
            return
      
        # comfyflowapp address
        app_server = config.get_option('server.address')
        if app_server is None or app_server == "":
            app_server = "localhost"
        app_port = int(id) + random.randint(10000, 20000)
        url = f"http://{app_server}:{app_port}"

        ret = start_app(name, id, url)
        st.session_state['app_start_ret'] = ret
        if ret == AppStatus.RUNNING.value:
            get_workspace_model().update_app_url(name, url)
            logger.info(f"App {name} is running yet, you could share {url} to your friends")
        elif ret == AppStatus.STARTED.value:
            get_workspace_model().update_app_url(name, url)
            logger.info(f"Start app {name} success, you could share {url} to your friends")
        else:
            logger.info(f"Start app {name} failed")
    else: 
        logger.warning(f"Please preview the app {name} first")

def click_stop_app(name, status, url):
    logger.info(f"stop app: {name} status: {status} url: {url}")
    if ready_start_app(status):
        if url == "":
            logger.info(f"App {name} url is empty, maybe it is stopped")
            st.session_state['app_stop_ret'] = AppStatus.STOPPED.value
        else:
            ret = stop_app(name, url)
            st.session_state['app_stop_ret'] = ret
            if ret == AppStatus.STOPPING.value:
                get_workspace_model().update_app_url(name, "")
                logger.info(f"Stop app {name} success, {url}")
            elif ret == AppStatus.STOPPED.value:
                get_workspace_model().update_app_url(name, "")
                logger.info(f"App {name} has stopped, {url}")
            else:
                logger.error(f"Stop app {name} failed, please check the log")
    else:
        logger.warning(f"Please preview the app {name} first")    


def create_operation_ui(app):
    id = app.id
    name = app.name
    status = app.status
    url = app.url
    disabled = True
    if st.session_state.get('username', 'anonymous') == app.username:
        disabled = False

    operate_row = row([1.2, 1.0, 1.1, 1.2, 1.0, 1.0, 1.1, 1.2, 1.2], vertical_align="bottom")
    preview_button = operate_row.button("✅ Preview", help="Preview and check the app", 
                                        key=f"{id}-button-preview", 
                                        on_click=click_preview_app, args=(app,), disabled=disabled)
    if preview_button:
        if not check_comfyui_alive():
            logger.warning("ComfyUI server is not alive, please check it")
            st.error(f"Preview app {name} failed, please check the log")
            st.stop()

    edit_button = operate_row.button("✏️ Edit", help="Edit the app", key=f"{id}-button-edit",
                                     on_click=click_edit_app, args=(app,), disabled=disabled)
    if edit_button:
        app_preview_ret = st.session_state['app_edit_ret']
        if app_preview_ret == AppStatus.ERROR.value:
            st.error(f"Edit app {name} failed, please check the log")

    if app.workflow_conf is not None:
        operate_row.download_button("💾 Export", data=app.workflow_conf, file_name=f"{app.name}_workflow.json", help="Export workflow to json", key=f"{id}-button-export",
                        disabled=disabled)
    else:
        operate_row.button("💾 Export", help="Export workflow to json", key=f"{id}-button-export", disabled=True)        

    install_button = operate_row.button("📲 Install", help="Install the app", key=f"{id}-button-install",
                                         on_click=click_install_app, args=(app,), disabled=disabled)
    if install_button:
        if status == AppStatus.CREATED.value:
            st.warning(f"Please preview the app {name} first")
        else:
            app_install_ret = st.session_state['app_install_ret']
            if app_install_ret == AppStatus.INSTALLED.value:
                st.success(f"App {name} has installed yet, you could use it at My Apps page")
            else:
                st.error(f"Install app {name} failed, please check the log")


    start_button = operate_row.button("▶️ Start", help="Start the app", key=f"{id}-button-start", 
                       on_click=click_start_app, args=(name, id, status), disabled=disabled)
    if start_button:
        if ready_start_app(status):
            app_preview_ret = st.session_state['app_start_ret']
            if app_preview_ret == AppStatus.RUNNING.value:
                st.info(f"App {name} is running yet, you could share {url} to your friends")
            elif app_preview_ret == AppStatus.STARTED.value:
                st.success(f"Start app {name} success, you could share {url} to your friends")
            else:
                st.error(f"Start app {name} failed")
        else:
            st.warning(f"Please preview the app {name} first")
        
    stop_button = operate_row.button("⏹️ Stop", help="Stop the app", key=f"{id}-button-stop",
                       on_click=click_stop_app, args=(name, status, url), disabled=disabled)
    if stop_button:
        if ready_start_app(status):
            app_stop_ret = st.session_state['app_stop_ret']
            if app_stop_ret == AppStatus.STOPPING.value:
                st.success(f"Stop app {name} success, {url}")
            elif app_stop_ret == AppStatus.STOPPED.value:
                st.success(f"App {name} has stopped, {url}")
            else:
                st.error(f"Stop app {name} failed, please check the log")
        else:
            st.warning(f"Please preview the app {name} first")        

    operate_row.markdown("")

    operate_row.button("🚮 Delete", help="Delete the app", key=f"{id}-button-delete", 
                       on_click=click_delete_app, args=(name,), disabled=disabled)
    
    publish_button = operate_row.button("✈️ Publish", help="Publish the app with template", 
                                        key=f"{id}-button-publish",
                                        on_click=click_publish_app, args=(app,), disabled=disabled)
    if publish_button:
        if status == AppStatus.CREATED.value:
            st.warning(f"Please preview the app {name} first")
        else:   
            if 'token_cookie' not in st.session_state:
                st.warning("Please go to homepage for your login :point_left:")


def is_load_workspace_page():
    if 'new_app' in st.session_state:
        return False
    if 'preview_app' in st.session_state:
        return False
    if 'publish_app' in st.session_state:
        return False
    if 'edit_app' in st.session_state:
        return False
    return True
        

logger.info("Loading workspace page")
page.page_init()                

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

    if 'new_app' in st.session_state:
        new_app_ui()
    elif 'edit_app' in st.session_state:
        edit_app_ui(app=st.session_state['edit_app'])
    elif 'preview_app' in st.session_state:
        preview_app_ui(st.session_state['preview_app'])
    elif 'publish_app' in st.session_state:    
        publish_app_ui(app=st.session_state['publish_app'], cookies=cookies)
    
    elif is_load_workspace_page():
        with page.stylable_button_container():
            header_row = row([0.85, 0.15], vertical_align="top")
            header_row.markdown("""
                ### My Workspace
                create and manage your comfyflowapps.
            """)
            new_app_button = header_row.button("New App", help="Create a new app from comfyui workflow.", on_click=click_new_app)

            if not st.session_state.get('username'):
                st.warning("Please go to homepage for your login :point_left:")
           
        with st.container():
            apps = get_workspace_model().get_all_apps()
            if len(apps) == 0:
                st.divider()
                st.info("No apps, please create a new app.")
            else:
                for app in apps:
                    st.divider()
                    logger.info(f"load app info {app}")
                    create_app_info_ui(app)
                    create_operation_ui(app)
            
            