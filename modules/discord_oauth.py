import os
from loguru import logger
import discordoauth2
import streamlit as st

client_id = os.environ['DISCORD_CLIENT_ID']
client_secret = os.environ['DISCORD_CLIENT_SECRET']
redirect_uri = os.environ['REDIRECT_URI']

client = discordoauth2.Client(client_id, secret=client_secret, redirect=redirect_uri)

@st.cache_resource
def get_client():
    return client

@st.cache_data(ttl=60 * 60)
def gen_authorization_url():
    client = get_client()
    authorization_url = client.generate_uri(scope=["identify", "email"])
    logger.debug(f"authorization_url: {authorization_url}")
    return authorization_url


def get_user_data(code):
    try:
        client = get_client()
        access = client.exchange_code(code)
        user_data = access.fetch_identify()
        logger.debug(f"user_data: {user_data}")
        return user_data
    except Exception as e:
        logger.error(f"get_user_data error: {e}")
        return None

