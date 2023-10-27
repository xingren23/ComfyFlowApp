from loguru import logger
import streamlit as st
from modules.page import page_init
from modules import get_sqlite_instance
from streamlit_extras.row import row

page_init()


def create_app_info_ui(app): 
    app_row = row([1, 5.4, 1.5, 1.1, 1], vertical_align="bottom")
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
    
    app_row.button("Download", help="Download app from app store", key=f"download_{app['id']}")
    app_row.button("Install", help="Install app into your apps", key=f"install_{app['id']}")

with st.container():
    with st.container():
        st.markdown("""
            ### App Store
        """)
        st.markdown("""
            This is a simple app store, you could explore and install apps from here.
        """)

    with st.container():
        apps = get_sqlite_instance().get_all_apps()
        for app in apps:
            st.divider()
            logger.info(f"load app info {app}")
            create_app_info_ui(app)

    