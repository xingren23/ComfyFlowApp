from loguru import logger

import streamlit as st
import modules.page as page
from templates.default import DefaultTemplate
from modules import get_sqlite_instance, get_comfy_client
from modules.sqlitehelper import AppStatus


logger.info("Loading release page")
page.page_init()

with st.container():
    st.title("✈️ Release and share your app to friends")

    apps = get_sqlite_instance().get_all_apps()
    app_name_map = {app['name']: app for app in apps if app['status'] == AppStatus.PREVIEWED.value} 
    preview_app_opts = list(app_name_map.keys())
    if len(preview_app_opts) == 0:
        st.warning("No app is available to release, please preview app first.")
    else:
        app_col, template_col = st.columns([0.3, 0.7])
        with app_col:
            with st.expander(":one: Select a app to release", expanded=True): 
                # select app
                # st.markdown("#### Select a app to release.")
                st.selectbox("My Apps", options=preview_app_opts, key="release_select_app", help="Select a app to preview")

            # release app
            with page.stylable_button_container():
                release_button = st.button("Release", help="Release your app with template", use_container_width=True) 
                if release_button:
                    release_app = st.session_state.get('release_select_app')
                    template_name = st.session_state.get('release_template_name')
                    logger.info(f"on_release_app: {release_app}, {template_name}")
                    # update app status
                    get_sqlite_instance().update_app_release(release_app, template_name)
                    st.success(f"Release {release_app} success") 

        with template_col:
            with st.expander(":two: Select a template for app", expanded=True):
                # select template
                st.markdown("#### Release with default template.")

                template_name = st.session_state.get('release_template_name')
                if template_name is None:
                    st.session_state['release_template_name'] = "default"

                # show template preview
                release_app = st.session_state.get('release_select_app')
                app = app_name_map[release_app]
                api_data = app['api_conf']
                app_data = app['app_conf']
                template = DefaultTemplate(comfy_client=get_comfy_client(), api_data=api_data, app_data=app_data)
                template.create_ui(disabled=True)
