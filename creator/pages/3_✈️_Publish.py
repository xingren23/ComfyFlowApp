from loguru import logger
import streamlit as st
import modules.page as page
from modules import get_sqlite_instance
from modules.sqlitehelper import AppStatus
from streamlit_extras.row import row
from streamlit_extras.switch_page_button import switch_page


logger.info("Loading publish page")
page.page_init()

with st.container():
    with page.stylable_button_container():
        header_row = row([0.85, 0.15], vertical_align="top")
        header_row.title("✈️ Publish and share to friends")
        back_button = header_row.button("Back Workspace", help="Back to your workspace", key='publish_back_workspace')
        if back_button:
            switch_page("Workspace")

    
    apps = get_sqlite_instance().get_all_apps()
    app_name_map = {app['name']: app for app in apps if app['status'] == AppStatus.PREVIEWED.value} 
    preview_app_opts = list(app_name_map.keys())
    if len(preview_app_opts) == 0:
        st.warning("No app is available to publish, please preview app first.")
        st.stop()
    else:
        with st.container():

            st.selectbox("My Apps", options=preview_app_opts, key='publish_select_app', help="Select a app to publish.")

            app = app_name_map[st.session_state['publish_select_app']]
            app_name = app['name']
            api_conf = app['api_conf']
            app_conf = app['app_conf']

            # edit app models

            # edit app nodes
