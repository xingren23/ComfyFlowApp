import os
from loguru import logger
import streamlit as st
import modules.page as page
from modules import get_sqlite_instance
from streamlit_extras.row import row
from streamlit_extras.switch_page_button import switch_page
from manager.app_manager import start_app, stop_app
from modules.sqlitehelper import AppStatus
from streamlit import config


def create_app_info_ui(app):
    app_row = row([1, 5.8, 2, 1.2], vertical_align="bottom")
    try:
        if app["image"] is not None:
            app_row.image(app["image"])
        else:
            app_row.image("./public/images/app-150.png")
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

    app_row.markdown(f"""
                    #### Web Site
                    🌐 {app['url']}
                    """)
       
    app_status = app['status']
    if app_status == AppStatus.CREATED.value:
        app_status = f"🌱 {app_status}"
    elif app_status == AppStatus.PREVIEWED.value:
        app_status = f"💡 {app_status}"
    elif app_status == AppStatus.PUBLISHED.value:
        app_status = f"✈️ {app_status}"
    app_row.markdown(f"""
                    #### Status
                    {app_status}
                    """)
    

def click_preview_app(name):
    logger.info(f"preview app: {name}")
    st.session_state['preview_select_app'] = name


def click_publish_app(name, status):
    logger.info(f"publish app: {name} status: {status}")
    st.session_state['publish_select_app'] = name
    

def click_delete_app(name):
    logger.info(f"delete app: {name}")
    get_sqlite_instance().delete_app(name)


def ready_start_app(status):
    if status == AppStatus.PREVIEWED.value or status == AppStatus.PUBLISHED.value:
        return True
    else:
        return False


def click_start_app(name, id, status):
    logger.info(f"start app: {name} status: {status}")
    if ready_start_app(status):
        server_addr = os.getenv('COMFYUI_SERVER_ADDR', default='localhost:8188')
        # comfyflowapp address
        app_server = config.get_option('server.address')
        if app_server is None or app_server == "":
            app_server = "localhost"
        app_port = int(server_addr.split(":")[1]) + int(id)
        url = f"http://{app_server}:{app_port}"

        ret = start_app(name, id, url)
        st.session_state['app_start_ret'] = ret
        if ret == AppStatus.RUNNING.value:
            get_sqlite_instance().update_app_url(name, url)
            logger.info(f"App {name} is running yet, you could share {url} to your friends")
        elif ret == AppStatus.STARTED.value:
            get_sqlite_instance().update_app_url(name, url)
            logger.info(f"Start app {name} success, you could share {url} to your friends")
        else:
            logger.info(f"Start app {name} failed")
    else: 
        logger.warning(f"Please preview this app {name} first")

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
                get_sqlite_instance().update_app_url(name, "")
                logger.info(f"Stop app {name} success, {url}")
            elif ret == AppStatus.STOPPED.value:
                get_sqlite_instance().update_app_url(name, "")
                logger.info(f"App {name} has stopped, {url}")
            else:
                logger.error(f"Stop app {name} failed, please check the log")
    else:
        logger.warning("Please preview this app first")

def create_operation_ui(app):
    id = app['id']
    name = app['name']
    status = app['status']
    url = app['url']
    operate_row = row([1.1, 0.9, 0.9, 4.9, 1.1, 1.1], vertical_align="bottom")
    preview_button = operate_row.button("💡Preview", help="Preview and check the app", 
                                        key=f"{id}-button-preview", 
                                        on_click=click_preview_app, args=(name,))
    if preview_button:
        switch_page("Preview")

    start_button = operate_row.button("▶️ Start", help="Start the app", key=f"{id}-button-start", 
                       on_click=click_start_app, args=(name, id, status))
    if start_button:
        if ready_start_app(status):
            app_start_ret = st.session_state['app_start_ret']
            if app_start_ret == AppStatus.RUNNING.value:
                st.info(f"App {name} is running yet, you could share {url} to your friends")
            elif app_start_ret == AppStatus.STARTED.value:
                st.success(f"Start app {name} success, you could share {url} to your friends")
            else:
                st.error(f"Start app {name} failed")
        else:
            st.warning("Please preview this app first")
        
    stop_button = operate_row.button("⏹️ Stop", help="Stop the app", key=f"{id}-button-stop",
                       on_click=click_stop_app, args=(name, status, url))
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
            st.warning("Please preview this app first")        

    operate_row.markdown("")

    operate_row.button("🗑 Delete", help="Delete the app", key=f"{id}-button-delete", 
                       on_click=click_delete_app, args=(name,))
    
    if status == AppStatus.PUBLISHED.value:
        operate_row.button("✈️ Publish", help="Publish the app with template", 
                                        key=f"{id}-button-publish",
                                        disabled=True)
    else:
        publish_button = operate_row.button("✈️ Publish", help="Publish the app with template", 
                                        key=f"{id}-button-publish",
                                        on_click=click_publish_app, args=(name, status,))
        if publish_button:
            if status == AppStatus.CREATED.value:
                st.error("Please preview and check this app first")
            else:
                switch_page("Publish")


logger.info("Loading workspace page")
page.page_init()                

with st.container():
    with page.stylable_button_container():
        header_row = row([0.88, 0.12], vertical_align="top")
        header_row.markdown("""
            ### My Workspace
        """)
        new_app_button = header_row.button("New App", help="Create a new app from comfyui workflow.")
        if new_app_button:
            switch_page("Create")

    with st.container():
        apps = get_sqlite_instance().get_all_apps()
        if len(apps) == 0:
            st.divider()
            st.info("No apps, please create a new app.")
        else:
            for app in apps:
                st.divider()
                logger.info(f"load app info {app}")
                create_app_info_ui(app)
                create_operation_ui(app)
            
            