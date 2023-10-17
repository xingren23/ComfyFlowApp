import os
import streamlit as st

def listdirs(dir_path):
    # listdirs from local path
    if not os.path.exists(dir_path):
        return []
    return [d for d in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, d))]


def get_apps():
    if 'comfyflow_apps' not in st.session_state.keys():
        from module.sqlitehelper import SQLiteHelper
        sqlitehelper = SQLiteHelper()
        apps = sqlitehelper.get_apps()
        st.session_state['comfyflow_apps'] = apps  
    return st.session_state['comfyflow_apps']