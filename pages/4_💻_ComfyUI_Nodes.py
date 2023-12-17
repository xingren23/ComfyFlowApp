import os
from loguru import logger
import modules.page as page
import streamlit as st
import requests

from modules import get_comfyflow_token
from streamlit_extras.row import row 


def on_click_new_key():
    if "new_key" not in st.session_state:
        st.session_state["new_key"] = True
    else:
        st.session_state.pop("new_key")

def get_node_list(session_cookie):
    api_url = f'{os.environ.get("COMFYFLOW_API_URL")}/api/node/list' 
    req = requests.get(api_url, cookies=session_cookie)
    if req.status_code == 200:
        logger.debug(f"get node list, {req.json()}")
        return req.json()
    else:
        return None
    
def get_active_nodes(session_cookie):
    api_url = f'{os.environ.get("COMFYFLOW_API_URL")}/api/node/actives' 
    req = requests.get(api_url, cookies=session_cookie)
    if req.status_code == 200:
        logger.debug(f"get active node list, {req.json()}")
        return req.json()
    else:
        return None
    
def submit_new_key(session_cookie, idx):
    keyname = st.session_state[f"{idx}_new_key_name"]
    logger.debug(f"click new key, {idx}, {keyname}")
    api_url = f'{os.environ.get("COMFYFLOW_API_URL")}/api/node/key/create'
    req = requests.post(api_url, cookies=session_cookie, json={"node_id": idx, "name": keyname})
    if req.status_code == 200:
        logger.info(f"New key created, {req.json()}")
        st.session_state['submit_new_key'] = "success"
        st.session_state['new_key_value'] = req.json()
    else:
        logger.error(f"New key created failed, {req.json()}")
        st.session_state['submit_new_key'] = "failed"

def submit_del_key(session_cookie, idx, key_id):
    logger.debug(f"click key delete, {idx}, {key_id}")
    api_url = f'{os.environ.get("COMFYFLOW_API_URL")}/api/node/key/delete'
    req = requests.post(api_url, cookies=session_cookie, json={"node_id": idx, "id": key_id})
    if req.status_code == 200:
        logger.info(f"New key created, {req.json()}")
    else:
        logger.error(f"New key created failed, {req.json()}")

def submit_new_node(session_cookie):
    logger.debug("click new node")
    node_name = st.session_state["new_node_name"]
    node_description = st.session_state["new_node_description"]
    node_endpoint = st.session_state["new_node_endpoint"]
    api_url = f'{os.environ.get("COMFYFLOW_API_URL")}/api/node/create'
    req = requests.post(api_url, cookies=session_cookie, 
                        json={"name": node_name,"description": node_description, "endpoint": node_endpoint})
    if req.status_code == 200:
        logger.info(f"New node created, {req.json()}")
    else:
        logger.error(f"New node created failed, {req.json()}")

def submit_active_node(session_cookie):
    logger.debug("click active node")
    invite_key = st.session_state["invite_node_key"]
    api_url = f'{os.environ.get("COMFYFLOW_API_URL")}/api/node/key/active'
    req = requests.post(api_url, cookies=session_cookie, json={"value": invite_key})
    if req.status_code == 200:
        logger.info(f"Node actived, {req.json()}")
    else:
        logger.error(f"Node actived failed, {req.json()}")

def click_delete_node(session_cookie, node_id):
    logger.debug(f"click delete node, {node_id}")
    api_url = f'{os.environ.get("COMFYFLOW_API_URL")}/api/node/delete'
    req = requests.post(api_url, cookies=session_cookie, json={"id": node_id})
    if req.status_code == 200:
        logger.info(f"Node deleted, {req.json()}")
    else:
        logger.error(f"Node deleted failed, {req.json()}")

def click_update_status(session_cookie, node_id, status):
    logger.debug(f"click update node status, {node_id}, {status}")
    api_url = f'{os.environ.get("COMFYFLOW_API_URL")}/api/node/update/status'
    req = requests.post(api_url, cookies=session_cookie, json={"id": node_id, "status": status})
    if req.status_code == 200:
        logger.info(f"update node status, {req.json()}")
    else:
        logger.error(f"update node status failed, {req.json()}")


def on_more_click(idx):
    logger.debug(f"click more, {idx}")
    st.session_state[f"show_keys_{idx}"] = True


def on_less_click(idx):
    logger.debug(f"click less, {idx}")
    st.session_state[f"show_keys_{idx}"] = False


logger.info("Loading node page")
page.page_init()

with st.container():
    if 'token_cookie' not in st.session_state:
        comfyflow_token = get_comfyflow_token()
        if comfyflow_token is not None:
            cookies = {'comfyflow_token': comfyflow_token}
            st.session_state['token_cookie'] = cookies
        else:
            cookies = None
    else:
        cookies = st.session_state['token_cookie']


    with st.container():
        st.header("""
                    Node
                    Manage your comfyui nodes, bind or activate comfyui node to comfyflowapp.
                    """)

        if not st.session_state.get('username'):
            st.error("Please go to homepage for your login :point_left:")
            st.stop()

        # active node list
        with st.container():
            active_nodes = get_active_nodes(cookies)

            st.divider()
            with page.stylable_button_container():
                active_row = row([0.85, 0.15], vertical_align="bottom")
                active_row.subheader(f"Your active node list, total {len(active_nodes)} nodes.")
                active_node_button = active_row.button("Active Node")
            if active_node_button:
                with st.form(key="active_node_form"):
                    st.text_input("Invite Key", key="invite_node_key")
                    st.form_submit_button("Active", type="primary", on_click=submit_active_node, args=[cookies])

            # active node list
            st.divider()
            node_row_header = row([0.4, 0.1, 0.15, 0.15, 0.1, 0.1], vertical_align="buttom")
            fields = ["Endpoint", "Status", "Invited By", "Actived By", "Actived", "Action"]
            # header
            for field in fields:
                node_row_header.write("**" + field + "**")

            for node in active_nodes:
                # node info
                node_info_row = row([0.4, 0.1, 0.15, 0.15, 0.1, 0.1], vertical_align="buttom")
                node_info_row.write(node["endpoint"])
                node_info_row.write(node["status"])
                node_info_row.write(node["invite_username"])
                node_info_row.write(node["active_username"])
                node_info_row.write(node["actived_at"].split("T")[0])
                    
                node_info_row.button("🗑", key=f"{node['id']}_active_delete", on_click=click_delete_node, args=[cookies, node["id"]])


        # my node list
        with st.container():
            nodes = get_node_list(cookies)
            
            st.divider()
            with page.stylable_button_container():
                nodes_row = row([0.85, 0.15], vertical_align="buttom")
                nodes_row.subheader(f"Your node list, total {len(nodes)} nodes.")
                new_node_button = nodes_row.button("New Node")
                if new_node_button:
                    with st.form(key="new_node_form"):
                        st.text_input("Node Name", key="new_node_name")
                        st.text_input("Node Description", key="new_node_description")
                        st.text_input("Node Endpoint", key="new_node_endpoint", help="comfyui node, e.g. https://{POD_ID}-{INTERNAL_PORT}.proxy.runpod.net")
                        st.form_submit_button("Submit", on_click=submit_new_node, args=[cookies])

            # node list
            for node in nodes:
                st.divider()
                node_row_header = row([0.2, 0.25, 0.3, 0.1, 0.15], vertical_align="buttom")
                fields = ["Name", "Description", "Endpoint", "Status", "Created"]
                # header
                for field in fields:
                    node_row_header.write("**" + field + "**")
                    
                # node info
                node_info_row = row([0.2, 0.25, 0.3, 0.1, 0.15], vertical_align="buttom")
                node_info_row.write(node["name"])
                node_info_row.write(node["description"])
                node_info_row.write(node["endpoint"])
                node_info_row.write(node["status"])
                node_info_row.write(node["created_at"].split("T")[0])
                    
                node_action_row = row([0.1, 0.1, 0.65, 0.15], vertical_align="buttom")
                if node["status"] == "enabled":
                    node_action_row.button("Disable", key=f"{node['id']}_disable", on_click=click_update_status, args=[cookies, node["id"], "disable"])
                elif node["status"] == "disabled" or node["status"] == "init":
                    node_action_row.button("Enable", key=f"{node['id']}_enable", on_click=click_update_status, args=[cookies, node["id"], "enabled"])
                node_action_row.button("Delete", key=f"{node['id']}_delete", on_click=click_delete_node, args=[cookies, node["id"]])
                node_action_row.write("")
                placeholder = node_action_row.empty()
                if st.session_state.get(f"show_keys_{node['id']}", False):
                    placeholder.button("Hidden Keys", key=f"{node['id']}_keys", on_click=on_less_click, args=[node["id"]])
                else:
                    placeholder.button("Show Keys", key=f"{node['id']}_keys", type="primary", on_click=on_more_click, args=[node["id"]])
                    
                if st.session_state.get(f"show_keys_{node['id']}", False):
                    logger.info(f"show_keys_{node['id']}")
                    node_keys_row = row([0.15, 0.25, 0.1, 0.1, 0.1, 0.1], vertical_align="buttom")
                    key_fields = ["Name", "Key", "InviteUser", "IsActived", "ActiveUser", "Action"]
                    # header
                    for field in key_fields:
                        node_keys_row.write("**" + field + "**")
                    # keys
                    for node_key in node["keys"]:                        
                        node_keys_row.write(node_key["name"])
                        node_keys_row.write(node_key["value"])
                        node_keys_row.write(node_key["invite_username"])
                        node_keys_row.checkbox(" ", value=node_key["status"] == "active", key=f"{node['id']}_{node_key['id']}_status")
                        node_keys_row.write(node_key["active_username"])
                        node_keys_row.button("🗑", key=f"{node['id']}_{node_key['id']}_del", on_click=submit_del_key, args=[cookies, node["id"], node_key["id"]])
                        
                    new_key_button = node_keys_row.button(f'Create a New Key', type="primary", key=f"{node['id']}_new", on_click=on_click_new_key)
                    if "new_key" in st.session_state:
                        with st.form(key=f"{node['id']}_new_key_form"):
                            st.text_input("Key Name", key=f"{node['id']}_new_key_name")
                            new_key_submit_button = st.form_submit_button("Submit", 
                                                                        on_click=submit_new_key, args=[cookies, node["id"]])
                        if new_key_submit_button:
                            if st.session_state.get("submit_new_key", None) == "success":
                                st.code(body=st.session_state['new_key_value']['value'], language="text")
                                st.success("Please copy the key value and save it, the key value will not be displayed again.")
                            else:
                                st.error("New key created failed.")
                            st.session_state.pop("new_key")
                            st.session_state.pop("submit_new_key")
