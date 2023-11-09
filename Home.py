import streamlit as st
from loguru import logger
from streamlit_extras.row import row
from modules import page
from modules.authenticate import MyAuthenticate

page.page_init(layout="centered")

with st.container():
    header_row = row([0.85, 0.15], vertical_align="bottom")
    header_row.markdown("""
        ## Welcome to ComfyFlowApp
        Develop a webapp from comfyui workflow in seconds, and share with others.
    """)
    logout_button = header_row.empty()   

    auth_instance =  MyAuthenticate("comfyflow_token", "ComfyFlowApp： Load ComfyUI workflow as webapp in seconds.")

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
                        ## 📌 What is ComfyFlowApp?
                        ComfyFlowApp is an extension tool for ComfyUI, making it easy to create a user-friendly application from a ComfyUI workflow and share it with others.
                        """)
            st.markdown("""
                        ### Why You Need ComfyFlowApp? 
                        If you need to share workflows developed in ComfyUI with other users, ComfyFlowApp can significantly lower the barrier for others to use your workflows:
                        - Users don't need to understand the principles of AI generation models. 
                        - Users don't need to know the tuning parameters of various AI models. 
                        - Users don't need to understand where to download models. 
                        - Users don't need to know how to set up ComfyUI workflows. 
                        - Users don't need to understand Python installation requirements.
                        
                        ComfyFlowApp helps application developers make these complexities transparent to users, who can use it like any other regular application.
                        """)
            st.markdown("""
                        ### Typical Use Cases
                        1) Studio or Internal Business Collaboration
                        2) Professional Creators or Teams, Developing and Sharing Applications with a Wider Audience
                        """)
            st.markdown("""
                        :point_right: Follow the repo [ComfyFlowApp](https://github.com/xingren23/ComfyFlowApp) to get the latest updates. 
                        
                        [!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/comfyflow)
                        """)
