import os
import streamlit as st
from streamlit_extras.row import row
from modules import page, get_auth_instance

page.page_init(layout="centered")

with st.container():
    header_row = row([0.85, 0.15], vertical_align="bottom")
    header_row.markdown("""
        ## Welcome to ComfyFlowApp
        Load comfyui workflow as webapp in seconds, and share with your friends.
    """)
    logout_button = header_row.empty()   


    auth_instance = get_auth_instance()
    if not st.session_state['authentication_status']:
        login_tab, reg_tab = st.tabs(["Login", "Register"])
        with login_tab:
            try:
                auth_instance.login("Login to ComfyFlowApp")
            except Exception as e:
                st.error(f"Login failed, {e}")
        with reg_tab:
            try:
                auth_instance.register_user("Register a new user of ComfyFlowApp", preauthorization=False)
            except Exception as e:
                st.error(f"Register failed, {e}")
    else: 
        with logout_button:
            auth_instance.logout("Logout")

        
        with st.container():
            name = st.session_state['name']
            username = st.session_state['username']
            st.markdown(f"Hello, {name}({username}) :smile:")
            
            st.markdown("""
                        ComfyFlowApp is an extension tool for ComfyUI. It helps convert ComfyUI workflows into web applications, making it easy for sharing with other users.

                        Workflow developers create workflows using ComfyUI by combining ComfyUI nodes and custom extension nodes. ComfyUI workflows can perform complex tasks like generating user avatars or changing product backgrounds for e-commerce. This addresses many real-world work needs. However, for regular users, building workflows can be quite complicated and time-consuming. 
                        
                        ComfyFlowApp simplifies the way workflows are shared and used. Workflow developers can easily share their workflows as webapp with others, however users don't need to worry about the inner details of the workflow. They can simply use the webapp.
            """)
            st.markdown("""
                        :point_right: Follow the repo [ComfyFlowApp](https://github.com/xingren23/ComfyFlowApp) to get the latest updates. 
                        
                        [!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/comfyflow)
                        """)
