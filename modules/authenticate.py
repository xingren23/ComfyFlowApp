from loguru import logger
import os
import requests
import streamlit as st
from streamlit_authenticator import Authenticate
from streamlit_authenticator.exceptions import RegisterError
from datetime import datetime, timedelta

class MyAuthenticate(Authenticate):
    def __init__(self, cookie_name: str, key:str, cookie_expiry_days: float=30.0):
        super().__init__({"usernames": {}}, cookie_name, key, cookie_expiry_days, [])
        self._check_cookie()
        st.session_state['comfyflow_token'] = self.get_token()
        self.comfyflow_url = os.getenv('COMFYFLOW_API_URL', default='https://api.comfyflow.app')
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
        
    
    def _update_password(self, username: str, password: str):
        # update password to remote
        pass

    def _register_credentials(self, username: str, name: str, password: str, email: str, invite_code: str, preauthorization: bool):
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

        if preauthorization:
            self.preauthorized['emails'].remove(email)

    def register_user(self, form_name: str, location: str = 'main', preauthorization=True) -> bool:
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
        if preauthorization:
            if not self.preauthorized:
                raise ValueError("preauthorization argument must not be None")
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
                        if preauthorization:
                            if new_email in self.preauthorized['emails']:
                                self._register_credentials(new_username, new_name, new_password, new_email, invite_code, preauthorization)
                                return True
                            else:
                                raise RegisterError('User not preauthorized to register')
                        else:
                            self._register_credentials(new_username, new_name, new_password, new_email, invite_code, preauthorization)
                            return True
                    else:
                        raise RegisterError('Passwords do not match')
                else:
                    raise RegisterError('Username already taken')
            else:
                raise RegisterError('Please enter an email, username, name, and password')

    def _set_random_password(self, username: str) -> str:
        # set random password to remote
        return "random_password"
    
    def _get_username(self, key: str, value: str) -> str:
        # get username from remote
        return "username"
    
    def _update_entry(self, username: str, key: str, value: str):
        # update entry to remote
        pass

    