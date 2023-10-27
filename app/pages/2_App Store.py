from loguru import logger
import time
import streamlit as st
from modules.page import page_init
from modules import get_sqlite_instance
from streamlit_extras.row import row
from threading import Thread
from modules.sqlitehelper import AppStatus
import queue

class InstallThread(Thread):
    def __init__(self, app, queue):
        super(InstallThread, self).__init__()
        self.app_id = app["id"]
        self.app_name = app["name"]
        self.app_api = app["api_conf"]
        self.queue = queue

    def parse_app_api(self):
        pass

    def dispatch_event(self, event):            
            if self.queue is not None:
                logger.debug(f"Dispatch event, {event}")
                self.queue.put(event)
            else:
                logger.info("queue is none")

    def run(self):
        try:
            logger.info(f"App {self.app_name} started to install")
            status_event = {'app_id': self.app_id, 'type': 'status', 
                            'data': {'info': f"App {self.app_name} started to download", 'state': 'running'}}
            self.dispatch_event(status_event)

            time.sleep(5)  
            status_event = {'app_id': self.app_id, 'type': 'status', 
                            'data': {'info': f"App {self.app_name} download finished", 'state': 'running'}}
            self.dispatch_event(status_event)

            time.sleep(1)
            status_event = {'app_id': self.app_id, 'type': 'status',
                            'data': {'info': f"App {self.app_name} started to install", 'state': 'running'}}
            self.dispatch_event(status_event)

            time.sleep(5)
            status_event = {'app_id': self.app_id, 'type': 'status',
                            'data': {'info': f"App {self.app_name} install finished", 'state': 'complete'}}
            self.dispatch_event(status_event)
            logger.info(f"App {self.app_name} installed")
        except Exception as e:
            logger.error(f"Install app error, {e}")
            status_event = {'app_id': self.app_id, 'type': 'status',
                            'data': {'info': f"App {self.app_name} install error", 'state': 'error'}}
            self.dispatch_event(status_event)


def install_app(app, queue):
    logger.info(f"Start install thread for {app['name']} ...")
    install_thread = InstallThread(app, queue)
    install_thread.start()
    
def update_install_progress(app, status_queue):
    get_sqlite_instance().update_app_status(app["id"], AppStatus.INSTALLING.value)
    with st.status(f"Waiting for install {app['name']} ...", state="running", expanded=True) as install_progress:
        while True:
            try:
                status_event = status_queue.get()
                logger.debug(f"Got install status event {status_event}")
                if status_event['type'] == 'status':
                    info = status_event['data']['info']
                    state = status_event['data']['state']
                    if state == 'running':
                        install_progress.write(info)
                    elif state == 'complete':
                        install_progress.write(info)
                        install_progress.update(label=f"Install app {app['name']} success", state="complete", expanded=False)
                        get_sqlite_instance().update_app_status(app["id"], AppStatus.INSTALLED.value)
                        break
                    elif state == 'error':
                        install_progress.write(info)
                        install_progress.update(label=f"Install app {app['name']} error", state="error", expanded=False)
                        get_sqlite_instance().update_app_status(app["id"], AppStatus.ERROR.value)
                        break
            except Exception as e:
                logger.warning(f"Queue get error {e}")
                continue

def show_install_status(app):
    if app["status"] == AppStatus.INSTALLING.value:
        st.info(f"App {app['name']} is installing ...")
    elif app["status"] == AppStatus.INSTALLED.value:
        st.success(f"App {app['name']} is installed")
    elif app["status"] == AppStatus.ERROR.value:
        st.error(f"App {app['name']} install error")

page_init()

def create_app_info_ui(app): 
    app_row = row([1, 6.8, 1.2, 1], vertical_align="bottom")
    try:
        if app["image"] is not None:
            app_row.image(app["image"])
        else:
            app_row.image("public/images/app-150.png")
    except Exception as e:
        logger.error(f"load app image error, {e}")

    # get description limit to 200 chars
    description = app["description"]
    if len(description) > 160:
        description = description[:160] + "..."                
    app_row.markdown(f"""
                    #### {app['name']}
                    {description}
                    """)
            
    app_author = "ComfyFlow"
    app_row.markdown(f"""
                    #### Author
                    {app_author}
                    """)
    
    app_status = app["status"]
    
    if f'{app["id"]}_progress_queue' not in st.session_state:
        status_queue = queue.Queue()
        st.session_state[f'{app["id"]}_progress_queue'] = status_queue
    status_queue = st.session_state.get(f'{app["id"]}_progress_queue')
    if app_status == AppStatus.RELEASED.value or app_status == AppStatus.ERROR.value:
        install_button = app_row.button("Install", help="Install app from app store",
                                         key=f"install_{app['id']}",
                                         on_click=install_app, args=(app, status_queue))
        if install_button:
            update_install_progress(app, status_queue)  

    elif app_status == AppStatus.INSTALLING.value or app_status == AppStatus.INSTALLED.value:
        reinstall_button = app_row.button("ReInstall", help="Install app from app store", 
                                          key=f"install_{app['id']}",
                                          on_click=install_app, args=(app, status_queue))
        if reinstall_button:
            update_install_progress(app, status_queue)

with st.container():
    with st.container():
        st.markdown("""
            ### App Store
        """)
        st.markdown("""
            This is a simple app store, you could explore and install apps from here.
        """)

    with st.container():
        apps = get_sqlite_instance().get_all_apps()
        for app in apps:
            st.divider()
            logger.info(f"load app info for {app['name']}")
            create_app_info_ui(app)
            show_install_status(app)

    