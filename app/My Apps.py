from loguru import logger
import streamlit as st
from modules import get_sqlite_instance
import modules.page as page
from streamlit_extras.row import row
from streamlit_extras.switch_page_button import switch_page

page.page_init()

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
        apps = get_sqlite_instance().get_all_apps()
        if len(apps) == 0:
            st.divider()
            st.info("No apps, you could explore and install app from the app store")
        else:
            for app in apps:
                logger.info(f"load app info {app}")

