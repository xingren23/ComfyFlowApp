from loguru import logger
from modules.comfyflow import Comfyflow
import streamlit as st
import modules.page as page
from streamlit_extras.row import row
from modules import get_comfy_client, get_workspace_model
from modules.workspace_model import AppStatus

def on_preview_workspace():
    st.session_state.pop('preview_app', None)
    logger.info("back to workspace")

def preview_app_ui(app):
    with page.stylable_button_container():
        header_row = row([0.85, 0.15], vertical_align="top")
        header_row.title("💡 Preview and check app")
        header_row.button("Back Workspace", help="Back to your workspace", key='preview_back_workspace', on_click=on_preview_workspace)

        # check user login
        if not st.session_state.get('username'):
            st.warning("Please go to homepage for your login :point_left:")
            st.stop()
        
    with st.container():
        name = app.name
        status = app.status
        api_data = app.api_conf
        app_data = app.app_conf
        comfy_client = get_comfy_client()
        comfyflow = Comfyflow(comfy_client=comfy_client, api_data=api_data, app_data=app_data)
        comfyflow.create_ui()
        if status == AppStatus.CREATED.value:
            if f"{name}_previewed" in st.session_state:
                previewed = st.session_state[f"{name}_previewed"]
                if previewed:
                    st.success(f"Preview app {name} success, you could install or publish the app at Workspace page.")
                    get_workspace_model().update_app_preview(name)
                    logger.info(f"update preview status for app: {name}")
                    st.stop()
                else:
                    st.warning(f"Preview app {name} failed.")


def on_back_apps():
    st.session_state.pop('enter_app', None)
    logger.info("back to my apps")

def enter_app_ui(app):
    with st.container():
        name = app.name
        description = app.description
        status = app.status
        logger.info(f"enter app {name}, status: {status}")

        with page.stylable_button_container():
            header_row = row([0.85, 0.15], vertical_align="top")
            header_row.title(f"{name}")
            header_row.button("My Apps", help="Back to your apps", key='enter_back_apps', on_click=on_back_apps)

        st.markdown(f"{description}")
        api_data = app.api_conf
        app_data = app.app_conf
        comfy_client = get_comfy_client()
        comfyflow = Comfyflow(comfy_client=comfy_client, api_data=api_data, app_data=app_data)
        comfyflow.create_ui(show_header=False)                                    