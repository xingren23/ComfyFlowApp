import streamlit as st
import requests
from loguru import logger
from streamlit_authenticator.exceptions import RegisterError
from streamlit_extras.row import row
from modules import page
from modules.authenticate import MyAuthenticate
from modules import discord_oauth
from modules.authenticate import Validator

def register_user(username: str, name: str, password: str, email: str, invite_code: str):
        logger.debug(f"register user, {username}, {name}, {password}, {email}")
        validator = Validator()
        # register credentials to comfyflowapp
        if not validator.validate_username(username):
            raise RegisterError('Username is not valid')
        if not validator.validate_name(name):
            raise RegisterError('Name is not valid')
        if not validator.validate_email(email):
            raise RegisterError('Email is not valid')
        if not len(password) >= 8:
            raise RegisterError('Password is not valid, length > 8')

        # register user
        register_json = {
            "nickname": name,
            "username": username,
            "password": password,
            "email": email,
            "invite_code": invite_code
        }
        comfyflow_url = st.secrets['COMFYFLOW_API_URL']
        ret = requests.post(f"{comfyflow_url}/api/user/register", json=register_json)
        if ret.status_code != 200:
            raise RegisterError(f"register user error, {ret.text}")
        else:
            logger.info(f"register user success, {ret.json()}")
            st.success(f"Register user success, {username}")

def gen_invite_code(source: str, uid: str):
    invate_code = f"oauth_{source}_{uid}"
    return invate_code
    
def back_home_login():
    st.session_state.pop('user_data', None)
    logger.info("back home login")


def discord_callback(user_data, header_button):
    with header_button:
        st.button("Login", key="home_button", on_click=back_home_login)

    st.write('''
        <h3>
            Register user with Discord
        </h3>''',
        unsafe_allow_html=True
    )
    with st.container():
        if user_data:
            register_user_form = st.form('Register user with Discord')
            # register_user_form.subheader(form_name)
            new_email = register_user_form.text_input('Email', value=user_data['email'], help='Please enter a valid email address')
            new_username = register_user_form.text_input('Username', value=user_data['username'], help='Please enter a username')
            new_name = register_user_form.text_input('Name', value=user_data['username'],help='Please enter your name')
            
            new_password = register_user_form.text_input('Password', type='password')
            new_password_repeat = register_user_form.text_input('Repeat password', type='password')

            invite_code = gen_invite_code("discord", user_data['id'])

            if register_user_form.form_submit_button('Register'):
                logger.debug(f"register user, {new_username}, {new_name}, {new_password}, {new_email}")
                if len(new_email) and len(new_username) and len(new_name) and len(new_password) > 0:
                    if new_password == new_password_repeat:
                        register_user(new_username, new_name, new_password, new_email, invite_code)
                    else:
                        raise RegisterError('Passwords do not match')
                else:
                    raise RegisterError('Please enter an email, username, name, and password')
        else:
            st.experimental_set_query_params()
            st.write('''
                <h3>
                    Login failed, go 
                    <a target="_self" href="/">Home</a>
                </h3>''',
                unsafe_allow_html=True
            )


def home(header_button):
    auth_instance =  MyAuthenticate("comfyflow_token", "ComfyFlowApp： Load ComfyUI workflow as webapp in seconds.")
    if not st.session_state['authentication_status']:
        with header_button:
            login_url = discord_oauth.gen_authorization_url()
            st.link_button("Register", url=login_url, help="Register with Discord")

        with st.container():
            try:
                auth_instance.login("Login to ComfyFlowApp")
            except Exception as e:  
                st.error(f"Login failed, {e}")
        
    else: 
        with header_button:
            auth_instance.logout("Logout")

        
        with st.container():
            name = st.session_state['name']
            username = st.session_state['username']
            st.markdown(f"Hello, {name}({username}) :smile:")
            
            st.markdown("""
                        ## 📌 What is ComfyFlowApp?
                        ComfyFlowApp is an extension tool for ComfyUI, making it easy to develop a user-friendly web application from a ComfyUI workflow and share it with others.
                        """)
            st.markdown("""
                        ### Why You Need ComfyFlowApp? 
                        ComfyFlowApp helps creator to develop a web app from comfyui workflow in seconds.

                        If you need to share workflows developed in ComfyUI with other users, ComfyFlowApp can significantly lower the barrier for others to use your workflows:
                        - Users don't need to understand the principles of AI generation models. 
                        - Users don't need to know the tuning parameters of various AI models. 
                        - Users don't need to understand where to download models. 
                        - Users don't need to know how to set up ComfyUI workflows. 
                        - Users don't need to understand Python installation requirements.
                        
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

page.init_env_default()
page.page_init(layout="centered")

with st.container():
    header_row = row([0.85, 0.15], vertical_align="bottom")
    header_row.markdown("""
        ## Welcome to ComfyFlowApp
        Develop a webapp from comfyui workflow in seconds, and share with others.
    """)
    header_button = header_row.empty()  

    code = st.experimental_get_query_params().get('code')
    if code:
        user_data = discord_oauth.get_user_data(code[0])
        st.session_state['user_data'] = user_data
        st.experimental_set_query_params()
    
    if 'user_data' in st.session_state:
        user_data = st.session_state['user_data']
        discord_callback(user_data=user_data, header_button=header_button)
    else:
        home(header_button) 
