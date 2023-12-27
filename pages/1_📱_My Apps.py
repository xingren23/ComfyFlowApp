from loguru import logger
import streamlit as st
import os
from modules import get_workspace_model
import modules.page as page
from streamlit_extras.row import row
from streamlit_extras.switch_page_button import switch_page
from modules import AppStatus, check_comfyui_alive
from modules.preview_app import enter_app_ui

def uninstall_app(app):
    logger.info(f"uninstall app {app.name}")
    get_workspace_model().update_app_uninstall(app.name)


def enter_app(app):
    logger.info(f"enter app {app.name}")
    st.session_state["enter_app"] = app


def create_app_info_ui(app):
    app_row = row([1, 5.4, 1.2, 1.4, 1], vertical_align="bottom")
    try:
        if app.image is not None:
            app_row.image(app.image)
        else:
            app_row.image("public/images/app-150.png")
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
    uninstall_button = app_row.button("🚮 Uninstall", help="Uninstall app from app store",
                                      key=f"uninstall_{app.id}", on_click=uninstall_app, args=(app,))
    if uninstall_button:
        logger.info(f"uninstall app {app.name}")
    
    enter_button = app_row.button("Enter", type='primary', help="Enter app to use", key=f"enter_{app.id}",
                                  on_click=enter_app, args=(app,))
    if enter_button:
        logger.info(f"enter app {app.name}")



page.page_init()

with st.container():
    
    container_empty = st.empty()
    if 'enter_app' in st.session_state:
        app = st.session_state['enter_app']
        logger.info(f"Start app ..., {app.name}")
        enter_app_ui(app)
    else:
        with page.stylable_button_container():
            header_row = row([0.85, 0.15], vertical_align="bottom")
            header_row.title("My Apps")
            explore_button = header_row.button(
                    "Install", help="Install more apps from your workspace.")
            if explore_button:
                switch_page("Workspace")

        with st.container():
            apps = get_workspace_model().get_installed_apps()
            if len(apps) == 0:
                st.divider()
                st.info("No apps, you could create and install app from your workspace")
            else:
                for app in apps:
                    st.divider()
                    logger.info(f"load app info for {app.name} {app}")
                    create_app_info_ui(app)
