import os
from loguru import logger
import streamlit as st
import module.page as page
from streamlit_extras.row import row
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.switch_page_button import switch_page

from module.utils import load_apps, init_comfyui
from manager.app_manager import start_app, stop_app


server_addr = os.getenv('COMFYUI_SERVER_ADDR', default='localhost:8188')   
logger.info(f"Loading workspace page, server_addr: {server_addr}")

page.page_header()

init_comfyui(server_addr)

with stylable_container(
        key="new_app_button",
        css_styles="""
            button {
                background-color: rgb(28 131 225);
                color: white;
                border-radius: 4px;
                width: 120px;
            }
            button:hover, button:focus {
                border: 0px solid rgb(28 131 225);
            }
        """,
    ):
    header_row = row([0.88, 0.12], vertical_align="bottom")
    header_row.markdown("""
    ### My Workspace
    """)
    new_button = header_row.button("New App", help="Create a new app from comfyui workflow.")
    if new_button:
        switch_page("Create")

with st.container():
    load_apps()
    apps = st.session_state['comfyflow_apps']
    if len(apps) == 0:
        st.divider()
        st.info("No apps, please create a new app.")
    else:
        for name in apps.keys():
            app = apps[name]
            st.divider()
            # get description limit to 200 chars
            description = app["description"]
            if len(description) > 160:
                description = description[:160] + "..."

            app_row = row([1, 5.8, 2,1.2], vertical_align="bottom")
            if app["image"] is not None:
                app_row.image(app["image"])
            else:
                app_row.image("https://via.placeholder.com/150")
            app_row.markdown(f"""
                            #### {app['name']}
                            {description}
                            """)
            app_row.markdown(f"""
                            #### Url
                            {app['url']}
                                """)
            app_status = f"🌱 {app['status']}"
            if app['status'] == "previewed":
                app_status = f"💡 {app['status']}"
            elif app['status'] == "released":
                app_status = f"✈️ {app['status']}"
            app_row.markdown(f"""
                            #### Status
                            {app_status}
                            """)
            operate_row = row([1, 1, 1, 4, 1, 1], vertical_align="bottom")
            # edit_button = operate_row.button(":apple: Edit", help="Edit this app.", key=f"{app['name']}-button-edit")
            # if edit_button:
            #     st.session_state.update({"edit_app": app['name']})
            #     switch_page("Create")
            preview_button = operate_row.button("💡Preview", help="Run this app.", key=f"{app['name']}-button-preview")
            if preview_button:
                st.session_state.update({"preview_app": app['name']})
                switch_page("Preview")
            release_button = operate_row.button("✈️Release", help="Share this app.", key=f"{app['name']}-button-release")
            if release_button:
                logger.info(f"release app: {app['name'], app['status']}")
                if app['status'] == "previewed":
                    st.session_state.update({"release_app": app['name']})
                    switch_page("Release")
                elif app['status'] == "created":
                    st.error("Please preview and check this app first.")
            delete_button = operate_row.button("🗑 Delete", help="Delete this app.", key=f"{app['name']}-button-delete")
            if delete_button:
                logger.info(f"delete app: {app['name']}")
                from module.sqlitehelper import sqlitehelper
                sqlitehelper.delete_app(app['name'])
                st.rerun()
            operate_row.markdown("")

            start_button = operate_row.button("▶️ Start", help="Start this app.", key=f"{app['name']}-button-start")
            if start_button:
                if app['status'] == "released":
                    logger.info(f"start app: {app['name'], app['url']}")
                    ret = start_app(app['name'], app['url'])
                    if ret == "running":
                        st.info(f"App {app['name']} is running yet, {app['url']}")
                    elif ret == "started":
                        st.success(f"Start app {app['name']} success, you could share {app['url']} to your friends")
                else:
                    st.error("Please release this app first.")
                
            stop_button = operate_row.button("⏹️ Stop", help="Stop this app.", key=f"{app['name']}-button-stop")
            if stop_button:
                if app['status'] == "released":
                    logger.info(f"stop app: {app['name']}")    
                    ret = stop_app(app['name'], app['url'])
                    if ret == "stopping":
                        st.success(f"Stop app {app['name']} success, {app['url']}")
                    elif ret == "stopped":
                        st.info(f"App {app['name']} has stopped, {app['url']}")
                else:
                    st.error("Please release this app first.")