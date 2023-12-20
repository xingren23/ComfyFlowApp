import os
from loguru import logger

import streamlit as st

client_id = os.getenv('DISCORD_CLIENT_ID')
client_secret = os.getenv('DISCORD_CLIENT_SECRET')
redirect_uri = os.getenv('DISCORD_REDIRECT_URI')


@st.cache_resource
def get_client():
    try:
        import discordoauth2
        client = discordoauth2.Client(client_id, secret=client_secret, redirect=redirect_uri)
        return client
    except Exception as e:
        logger.error(f"get_client error: {e}")
        return None
   

@st.cache_data(ttl=60 * 60)
def gen_authorization_url():
    client = get_client()
    if client:
        authorization_url = client.generate_uri(scope=["identify", "email"])
        logger.debug(f"authorization_url: {authorization_url}")
        return authorization_url
    else:
        authorization_url = f"https://discord.com/oauth2/authorize?client_id={client_id}&scope=identify+email&redirect_uri={redirect_uri}&response_type=code"
        logger.warning(f"discordoauth2 is none, default authorization_url : {authorization_url}")   
        return authorization_url


def get_user_data(code):
    try:
        client = get_client()
        if client:
            access = client.exchange_code(code)
            user_data = access.fetch_identify()
            logger.debug(f"user_data: {user_data}")
            return user_data
    except Exception as e:
        logger.error(f"get_user_data error: {e}")
        return None

