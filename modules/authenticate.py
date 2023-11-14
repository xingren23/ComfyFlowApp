from loguru import logger
import os
import re
import jwt
import requests
import streamlit as st
from streamlit_authenticator.exceptions import RegisterError
from datetime import datetime, timedelta
import extra_streamlit_components as stx

class Validator:
    """
    This class will check the validity of the entered username, name, and email for a 
    newly registered user.
    """
    def validate_username(self, username: str) -> bool:
        """
        Checks the validity of the entered username.
        """
        pattern = r"^[a-zA-Z0-9_-]{1,20}$"
        return bool(re.match(pattern, username))

    def validate_name(self, name: str) -> bool:
        """
        Checks the validity of the entered name.
        """
        return 1 < len(name) < 100

    def validate_email(self, email: str) -> bool:
        """
        Checks the validity of the entered email.
        """
        return "@" in email and 2 < len(email) < 320
    
class MyAuthenticate():
    def __init__(self, cookie_name: str, key:str, cookie_expiry_days: float=30.0):
        self.cookie_name = cookie_name
        self.key = key
        self.cookie_expiry_days = cookie_expiry_days
        self.cookie_manager = stx.CookieManager()
        self.validator = Validator()

        if 'name' not in st.session_state:
            st.session_state['name'] = None
        if 'authentication_status' not in st.session_state:
            st.session_state['authentication_status'] = None
        if 'username' not in st.session_state:
            st.session_state['username'] = None
        if 'logout' not in st.session_state:
            st.session_state['logout'] = None

        self._check_cookie()
        st.session_state['comfyflow_token'] = self.get_token()
        self.comfyflow_url = os.getenv('COMFYFLOW_API_URL')
        logger.info(f"username {st.session_state['username']}")
        
    def get_token(self) -> str:
        """
        Gets the token from the cookie.

        Returns
        -------
        str
            The token.
        """
        return self.cookie_manager.get(self.cookie_name)
    
    def _token_encode(self) -> str:
        """
        Encodes the contents of the reauthentication cookie.

        Returns
        -------
        str
            The JWT cookie for passwordless reauthentication.
        """
        return jwt.encode({'name':st.session_state['name'],
            'username':st.session_state['username'],
            'exp_date':self.exp_date}, self.key, algorithm='HS256')

   
    def _token_decode(self) -> str:
        """
        Decodes the contents of the reauthentication cookie.

        Returns
        -------
        str
            The decoded JWT cookie for passwordless reauthentication.
        """
        try:
            return jwt.decode(self.token, self.key, algorithms=['HS256'])
        except:
            return False

    def _set_exp_date(self) -> str:
        """
        Creates the reauthentication cookie's expiry date.

        Returns
        -------
        str
            The JWT cookie's expiry timestamp in Unix epoch.
        """
        return (datetime.utcnow() + timedelta(days=self.cookie_expiry_days)).timestamp()
    
    def _check_pw(self) -> bool:
        # check username and password 
        username = self.username
        login_json = {
            "username": username,
            "password": self.password
        }
        ret = requests.post(f"{self.comfyflow_url}/api/user/login", json=login_json)
        if ret.status_code != 200:
            logger.error(f"login error, {ret.text}")
            st.error(f"Login failed, {ret.text}")
            return False
        else:
            st.session_state['username'] = ret.json()['username']
            st.session_state['name'] = ret.json()['nickname']

            logger.info(f"login success, {ret.text}")
            st.success(f"Login success, {username}")
            return True
    
    def _check_credentials(self, inplace: bool = True) -> bool:
        try:
            if self._check_pw():
                if inplace:
                    self.exp_date = self._set_exp_date()
                    self.token = self._token_encode()
                    st.session_state['token'] = self.token
                    self.cookie_manager.set(self.cookie_name, self.token,
                            expires_at=datetime.now() + timedelta(days=self.cookie_expiry_days))
                    st.session_state['authentication_status'] = True
                else:
                    return True
            else:
                if inplace:
                    st.session_state['authentication_status'] = False
                else:
                    return False
        except Exception as e:
            logger.error(f"check credentials error, {e}")
        
    def login(self, form_name: str, location: str='main') -> tuple:
        """
        Creates a login widget.

        Parameters
        ----------
        form_name: str
            The rendered name of the login form.
        location: str
            The location of the login form i.e. main or sidebar.
        Returns
        -------
        str
            Name of the authenticated user.
        bool
            The status of authentication, None: no credentials entered, 
            False: incorrect credentials, True: correct credentials.
        str
            Username of the authenticated user.
        """
        if location not in ['main', 'sidebar']:
            raise ValueError("Location must be one of 'main' or 'sidebar'")
        if not st.session_state['authentication_status']:
            self._check_cookie()
            if not st.session_state['authentication_status']:
                if location == 'main':
                    login_form = st.form('Login')
                elif location == 'sidebar':
                    login_form = st.sidebar.form('Login')

                login_form.subheader(form_name)
                self.username = login_form.text_input('Username')
                st.session_state['username'] = self.username
                self.password = login_form.text_input('Password', type='password')

                if login_form.form_submit_button('Login'):
                    self._check_credentials()

    def logout(self, button_name: str, location: str='main', key: str=None):
        """
        Creates a logout button.

        Parameters
        ----------
        button_name: str
            The rendered name of the logout button.
        location: str
            The location of the logout button i.e. main or sidebar.
        """
        if location not in ['main', 'sidebar']:
            raise ValueError("Location must be one of 'main' or 'sidebar'")
        if location == 'main':
            if st.button(button_name, key):
                self.cookie_manager.delete(self.cookie_name)
                st.session_state['logout'] = True
                st.session_state['name'] = None
                st.session_state['username'] = None
                st.session_state['authentication_status'] = None
        elif location == 'sidebar':
            if st.sidebar.button(button_name, key):
                self.cookie_manager.delete(self.cookie_name)
                st.session_state['logout'] = True
                st.session_state['name'] = None
                st.session_state['username'] = None
                st.session_state['authentication_status'] = None

    def _check_cookie(self):
        """
        Checks the validity of the reauthentication cookie.
        """
        self.token = self.cookie_manager.get(self.cookie_name)
        if self.token is not None:
            self.token = self._token_decode()
            if self.token is not False:
                if not st.session_state['logout']:
                    if self.token['exp_date'] > datetime.utcnow().timestamp():
                        if 'name' and 'username' in self.token:
                            st.session_state['name'] = self.token['name']
                            st.session_state['username'] = self.token['username']
                            st.session_state['authentication_status'] = True

    def _register_credentials(self, username: str, name: str, password: str, email: str, invite_code: str = ""):
        # register credentials to comfyflowapp
        if not self.validator.validate_username(username):
            raise RegisterError('Username is not valid')
        if not self.validator.validate_name(name):
            raise RegisterError('Name is not valid')
        if not self.validator.validate_email(email):
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
        ret = requests.post(f"{self.comfyflow_url}/api/user/register", json=register_json)
        if ret.status_code != 200:
            raise RegisterError(f"register user error, {ret.text}")
        else:
            logger.info(f"register user success, {ret.json()}")
            st.success(f"Register user success, {username}")


    def register_user_info(self, form_name: str, location: str = 'main', data: dict={}) -> bool:
        if location not in ['main', 'sidebar']:
            raise ValueError("Location must be one of 'main' or 'sidebar'")
        if location == 'main':
            register_user_form = st.form('Register user')
        elif location == 'sidebar':
            register_user_form = st.sidebar.form('Register user')

        register_user_form.subheader(form_name)
        new_email = register_user_form.text_input('Email', value=data['email'], help='Please enter a valid email address')
        new_username = register_user_form.text_input('Username', value=data['username'], help='Please enter a username')
        new_name = register_user_form.text_input('Name', value=data['username'],help='Please enter your name')
        
        new_password = register_user_form.text_input('Password', type='password')
        new_password_repeat = register_user_form.text_input('Repeat password', type='password')

        if register_user_form.form_submit_button('Register'):
            if len(new_email) and len(new_username) and len(new_name) and len(new_password) > 0:
                if new_username not in self.credentials['usernames']:
                    if new_password == new_password_repeat:
                        self._register_credentials(new_username, new_name, new_password, new_email)
                        return True
                    else:
                        raise RegisterError('Passwords do not match')
                else:
                    raise RegisterError('Username already taken')
            else:
                raise RegisterError('Please enter an email, username, name, and password')



    def register_user(self, form_name: str, location: str = 'main') -> bool:
        """
        Creates a register new user widget, add field: invite_code

        Parameters
        ----------
        form_name: str
            The rendered name of the register new user form.
        location: str
            The location of the register new user form i.e. main or sidebar.
        preauthorization: bool
            The preauthorization requirement, True: user must be preauthorized to register, 
            False: any user can register.
        Returns
        -------
        bool
            The status of registering the new user, True: user registered successfully.
        """
        if location not in ['main', 'sidebar']:
            raise ValueError("Location must be one of 'main' or 'sidebar'")
        if location == 'main':
            register_user_form = st.form('Register user')
        elif location == 'sidebar':
            register_user_form = st.sidebar.form('Register user')

        register_user_form.subheader(form_name)
        new_email = register_user_form.text_input('Email', help='Please enter a valid email address')
        new_username = register_user_form.text_input('Username', help='Please enter a username')
        new_name = register_user_form.text_input('Name', help='Please enter your name')
        invite_code = register_user_form.text_input('Invite code', help='Please enter an invite code')
        new_password = register_user_form.text_input('Password', type='password')
        new_password_repeat = register_user_form.text_input('Repeat password', type='password')

        if register_user_form.form_submit_button('Register'):
            if len(new_email) and len(new_username) and len(new_name) and len(new_password) > 0:
                if new_username not in self.credentials['usernames']:
                    if new_password == new_password_repeat:
                        self._register_credentials(new_username, new_name, new_password, new_email, invite_code)
                        return True
                    else:
                        raise RegisterError('Passwords do not match')
                else:
                    raise RegisterError('Username already taken')
            else:
                raise RegisterError('Please enter an email, username, name, and password')


    