import os
from loguru import logger
import streamlit as st
from modules import get_sqlite_instance, get_comfy_client
import modules.page as page
from streamlit_extras.row import row
from streamlit_extras.switch_page_button import switch_page
import subprocess   

def uninstall_app(app):
    logger.info(f"uninstall app {app['name']}")
    get_sqlite_instance().delete_app(app["id"])

def enter_app(app):
    logger.info(f"enter app {app['name']}")
    st.session_state["current_app"] = app

def create_app_info_ui(app): 
    app_row = row([1, 5.8, 1.2, 1, 1], vertical_align="bottom")
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
    uninstall_button = app_row.button("Uninstall", help="Uninstall app from app store",
                                       key=f"uninstall_{app['id']}", on_click=uninstall_app, args=(app,))
    if uninstall_button:
        logger.info(f"uninstall app {app['name']}")
    enter_button = app_row.button("Enter", type='primary', help="Enter app to use", key=f"enter_{app['id']}", 
                                  on_click=enter_app, args=(app,))
    if enter_button:
        logger.info(f"enter app {app['name']}")

def check_comfyui_alive():
    try:
        get_comfy_client().queue_remaining()
        return True
    except Exception as e:
        logger.error(f"check comfyui alive error, {e}")
        return False
    
def start_comfyui():
    try:
        if check_comfyui_alive():
            logger.info("comfyui is alive")
            return True

        logger.info("start comfyui")
        server_addr = os.getenv('COMFYUI_SERVER_ADDR', default='localhost:8188')
        address, port = server_addr.split(":")
        command = f"python3 main.py --server.port {port} --server.address {address}"
        path = "repositories/ComfyUI"
        result = subprocess.run(command, shell=True, cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            logger.info("start comfyui output:", result.stdout)
            return True
        else:
            logger.warning(f"start comfyui {command} return ", result.stderr)
            return False
    except Exception as e:
        logger.error(f"start comfyui error, {e}")

page.page_init()

with st.container():
    container_empty = st.empty()
    if 'current_app' in st.session_state:
        with container_empty:
            with st.container():
                app = st.session_state.get('current_app')
                logger.info(f"enter app {app['name']}")
                app_data = app['app_conf']
                api_data = app['api_conf']

                # check comfyui is alive                
                if not start_comfyui():
                    st.error("start comfyui error.")
                    st.stop()

                from modules.comfyflow import Comfyflow
                comfy_flow = Comfyflow(comfy_client=get_comfy_client(), api_data=api_data, app_data=app_data)
                comfy_flow.create_ui()
    else:   
        with container_empty:
            with st.container():
                with page.stylable_button_container():
                    header_row = row([0.85, 0.15], vertical_align="bottom")
                    header_row.markdown("""
                        ### My Apps
                    """)
                    new_app_button = header_row.button("Explore Apps", help="Explore more apps from app store.")
                    if new_app_button:
                        switch_page("App Store")

                with st.container():
                    apps = get_sqlite_instance().get_my_apps()
                    if len(apps) == 0:
                        st.divider()
                        st.info("No apps, you could explore and install app from the app store")
                    else:
                        for app in apps:
                            st.divider()
                            logger.info(f"load app info for {app['name']}")
                            create_app_info_ui(app)

