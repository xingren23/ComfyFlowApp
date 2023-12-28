import streamlit as st
import requests
import os
from loguru import logger
from streamlit_authenticator.exceptions import RegisterError
from streamlit_extras.row import row
from modules import page
from modules.authenticate import MyAuthenticate
from modules.authenticate import Validator


def gen_invite_code(source: str, uid: str):
    invate_code = f"oauth_{source}_{uid}"
    return invate_code
    
def back_home_signup():
    st.session_state.pop('user_data', None)
    logger.info("back home login")


page.init_env_default()
page.page_init(layout="centered")

with st.container():
    header_row = row([0.87, 0.13], vertical_align="bottom")
    header_row.title("""
        Welcome to ComfyFlowApp
        From comfyui workflow to web application in seconds, and share with others.
    """)
    header_button = header_row.empty()  

    auth_instance =  MyAuthenticate("comfyflow_token", "ComfyFlowApp： Load ComfyUI workflow as webapp in seconds.")
    if not st.session_state['authentication_status']:
        with header_button:
            client_id = os.getenv('DISCORD_CLIENT_ID')
            redirect_uri = os.getenv('DISCORD_REDIRECT_URI')
            signup_url = f"https://discord.com/oauth2/authorize?client_id={client_id}&scope=identify+email&redirect_uri={redirect_uri}&response_type=code"
            st.link_button("Sign Up", type="primary", url=signup_url, help="Sign up with Discord")

        with st.container():
            try:
                st.markdown("ComfyFlowApp offers an in-built test account(username: demo) with the credentials(password: comfyflowapp). For an enhanced user experience, please sign up your account at https://comfyflow.app.")
                auth_instance.login("Login to ComfyFlowApp")
            except Exception as e:  
                st.error(f"Login failed, {e}")
        
    else: 
        with header_button:
            auth_instance.logout(button_name="Logout", location="main", key="home_logout_button")

        
        with st.container():
            name = st.session_state['name']
            username = st.session_state['username']
            st.markdown(f"Hello, {name}({username}) :smile:")
            
            st.markdown("""
                        ### 📌 What is ComfyFlowApp?
                        ComfyFlowApp is an extension tool for ComfyUI, making it easy to develop a user-friendly web application from a ComfyUI workflow and share it with others.
                        """)
            st.markdown("""
                        ### 📌 Why You Need ComfyFlowApp? 
                        ComfyFlowApp helps creator to develop a web app from comfyui workflow in seconds.

                        If you need to share workflows developed in ComfyUI with other users, ComfyFlowApp can significantly lower the barrier for others to use your workflows:
                        - Users don't need to understand the principles of AI generation models. 
                        - Users don't need to know the tuning parameters of various AI models. 
                        - Users don't need to understand where to download models. 
                        - Users don't need to know how to set up ComfyUI workflows. 
                        - Users don't need to understand Python installation requirements.
                        
                        """)
            st.markdown("""
                        ### 📌 Use Cases
                        """)
            st.image("./docs/images/how-to-use-it.png", use_column_width=True)
            st.markdown("""
                        :point_right: Follow the repo [ComfyFlowApp](https://github.com/xingren23/ComfyFlowApp) to get the latest updates. 
                        """)
