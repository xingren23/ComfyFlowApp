from loguru import logger
import streamlit as st


@st.cache_resource
def get_sqlite_instance():
    logger.info("get_sqlite_instance")
    from modules.sqlitehelper import SQLiteHelper
    sqliteInstance = SQLiteHelper()      
    return sqliteInstance