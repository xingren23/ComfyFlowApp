from loguru import logger

import streamlit as st
import module.page as page


def init_apps():
    if 'comfyflow_apps' not in st.session_state.keys():
        from module.sqlitehelper import SQLiteHelper
        sqlitehelper = SQLiteHelper()
        apps = sqlitehelper.get_apps()
        st.session_state['comfyflow_apps'] = apps

logger.info("Loading home page")

page.page_header()

init_apps()

with st.container():
    st.markdown("## 📌 Welcome to ComfyFlowApp")
    st.markdown("""
                        ComfyFlowApp is an extension tool for ComfyUI. It helps convert ComfyUI workflows into web applications, making it easy for sharing with other users.

                        Workflow developers create workflows using ComfyUI by combining ComfyUI nodes and custom extension nodes. ComfyUI workflows can perform complex tasks like generating user avatars or changing product backgrounds for e-commerce. This addresses many real-world work needs. However, for regular users, building workflows can be quite complicated and time-consuming. 
                        
                        ComfyFlowApp simplifies the way workflows are shared and used. Workflow developers can easily share their workflows as webapp with others, however users don't need to worry about the inner details of the workflow. They can simply use the webapp.
            """)
    st.markdown("""
                        :point_right: Follow the repo [ComfyFlowApp](https://github.com/xingren23/ComfyFlowApp) to get the latest updates. 
                        
                        [!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/comfyflow)
                        """)
    st.markdown("""
                        ### How to develop a ComfyFlowApp?
                        """)
    st.markdown("""
                        :one: Develop：develop workflow in ComfyUI, refer to [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
                        """)
    st.image('./docs/images/comfy-workflow.png',
             caption='ComfyUI workflow')
    st.markdown("""
                        :two: Upload：upload workflow image to ComfyFlowApp, and configure application parameters to generate WebApp application
                        """)
    st.image('./docs/images/comfy-upload-app.png',
             caption='Upload workflow image')
    st.markdown("""
                        :three: Preview：preview WebApp application online
                        """)
    st.image('./docs/images/comfy-workflow-app.png',
             caption='Preview WebApp application')

    st.markdown("""
                        ### Some examples
                        **👈 Select a demo from the Workflow page on the left** to see some examples of ComfyFlowApp can do!
                        """)
