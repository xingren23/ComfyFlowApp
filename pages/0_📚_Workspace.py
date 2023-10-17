from loguru import logger
import streamlit as st
import module.header as header
from streamlit_extras.row import row
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.switch_page_button import switch_page

from module.utils import get_apps

logger.info("Loading workspace page")
header.page_header()


with stylable_container(
        key="new_app_button",
        css_styles="""
            button {
                background-color: rgb(28 131 225);
                color: white;
                border-radius: 4px;
                width: 120px;
            }
            button:hover {
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
    apps = get_apps()
    for app in apps:
        st.divider()
        # get description limit to 200 chars
        description = app["description"]
        if len(description) > 160:
            description = description[:160] + "..."

        app_row = row([1, 5, 1,1,1,1], vertical_align="bottom")
        app_row.image(app["image"])
        app_row.markdown(f"""
                         ### {app['name']}
                        {description}
                        {app['url']}
                          """)
        
        edit_button = app_row.button(":apple: Edit", help="Edit this app.", key=f"{app['name']}-button-edit")
        if edit_button:
            st.session_state.update({"edit_app": app['name']})
            switch_page("Create")
        preview_button = app_row.button("Preview", help="Run this app.", key=f"{app['name']}-button-preview")
        if preview_button:
            st.session_state.update({"preview_app": app['name']})
            switch_page("Preview")
        release_button = app_row.button("Release", help="Share this app.", key=f"{app['name']}-button-release")
        if release_button:
            if True:
                st.session_state.update({"release_app": app['name']})
                switch_page("Release")
            else:
                st.error("You need to preview and check the app first.")
        delete_button = app_row.button("Delete", help="Delete this app.", key=f"{app['name']}-button-delete")
