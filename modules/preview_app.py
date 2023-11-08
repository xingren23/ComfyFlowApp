from loguru import logger
from modules.comfyflow import Comfyflow

import streamlit as st
import modules.page as page
from streamlit_extras.row import row
from streamlit_extras.switch_page_button import switch_page
from modules import get_comfy_client, get_workspace_model
from modules.workspace import AppStatus

def on_new_workspace():
    st.session_state['preview_app'] = False

def preview_app_ui():
    with page.stylable_button_container():
        header_row = row([0.85, 0.15], vertical_align="top")
        header_row.title("💡 Preview and check app")
        header_row.button("Back Workspace", help="Back to your workspace", key='preview_back_workspace', on_click=on_new_workspace)

    apps = get_workspace_model().get_all_apps()
    app_name_map = {app.name: app for app in apps}
    app_opts = list(app_name_map.keys())
    if len(app_opts) == 0:
        st.warning("Please create a new app first.")
        st.stop()
    else:
        st.selectbox("My Apps", options=app_opts, key='preview_select_app', help="Select a app to preview.")
        
        preview_app = st.session_state['preview_select_app']
        if preview_app:
            logger.info(f"preview app: {preview_app}")
            
            app = app_name_map[preview_app]
            status = app.status
            api_data = app.api_conf
            app_data = app.app_conf
            comfyflow = Comfyflow(comfy_client=get_comfy_client(), api_data=api_data, app_data=app_data)
            comfyflow.create_ui(show_header=False)
            if status == AppStatus.CREATED.value:
                if f"{preview_app}_previewed" in st.session_state:
                    previewed = st.session_state[f"{preview_app}_previewed"]
                    if previewed:
                        st.success(f"Preview app {preview_app} success, back to workspace, you could start or publish the app.")
                        get_workspace_model().update_app_preview(preview_app)
                        logger.info(f"update preview status for app: {preview_app}")
                        st.stop()
                    else:
                        st.warning(f"Preview app {preview_app} failed.")
                    

                        