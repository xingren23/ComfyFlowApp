import os
from loguru import logger
import streamlit as st
import modules.page as page
from streamlit_extras.row import row
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.switch_page_button import switch_page

from modules.utils import load_apps
from manager.app_manager import start_app, stop_app


logger.info("Loading workspace page")

page.page_header()

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
        from modules.sqlitehelper import sqlitehelper
        for name in apps.keys():
            app = apps[name]
            st.divider()
            # get description limit to 200 chars
            description = app["description"]
            if len(description) > 160:
                description = description[:160] + "..."

            app_row = row([1, 5.8, 1.2, 2], vertical_align="bottom")
            if app["image"] is not None:
                app_row.image(app["image"])
            else:
                app_row.image("https://via.placeholder.com/150")
            app_row.markdown(f"""
                            #### {app['name']}
                            {description}
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
            app_row.markdown(f"""
                            #### Web Site
                            🌐 {app['url']}
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
                sqlitehelper.delete_app(app['name'])
                st.rerun()
            operate_row.markdown("")

            start_button = operate_row.button("▶️ Start", help="Start this app.", key=f"{app['name']}-button-start")
            if start_button:
                if app['status'] == "released":
                    server_addr = os.getenv('COMFYUI_SERVER_ADDR', default='localhost:8188')
                    app_port = int(server_addr.split(":")[1]) + int(app['id'])
                    url = f"http://localhost:{app_port}"

                    ret = start_app(app['name'], url)
                    if ret == "running":
                        sqlitehelper.update_app_url(app['name'], url)
                        logger.info(f"App {app['name']} is running yet, {app['url']}")
                        st.rerun()
                    elif ret == "started":
                        sqlitehelper.update_app_url(app['name'], url)
                        logger.info(f"Start app {app['name']} success, you could share {app['url']} to your friends")
                        st.rerun()
                    else:
                        st.error(f"Start app {app['name']} failed, please check the log")
                    
                else:
                    st.error("Please release this app first.")
                
            stop_button = operate_row.button("⏹️ Stop", help="Stop this app.", key=f"{app['name']}-button-stop")
            if stop_button:
                if app['status'] == "released":
                    logger.info(f"stop app: {app['name']}")    
                    if app['url'] == "":
                        st.info(f"App {app['name']} url is empty, maybe it is stopped")
                    else:
                        ret = stop_app(app['name'], app['url'])
                        if ret == "stopping":
                            sqlitehelper.update_app_url(app['name'], "")
                            logger.info(f"Stop app {app['name']} success, {app['url']}")
                            st.rerun()
                        elif ret == "stopped":
                            sqlitehelper.update_app_url(app['name'], "")
                            logger.info(f"App {app['name']} has stopped, {app['url']}")
                            st.rerun()
                        else:
                            st.error(f"Stop app {app['name']} failed, please check the log")
                    
                else:
                    st.error("Please release this app first.")