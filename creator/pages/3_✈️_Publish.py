from loguru import logger
import json
import re
import streamlit as st
import modules.page as page
from modules import get_sqlite_instance
from modules.sqlitehelper import AppStatus
from streamlit_extras.row import row
from streamlit_extras.switch_page_button import switch_page

def parsed_model_url(model_url, save_path):
    # parse model info from download url, 
    # eg: https://huggingface.co/segmind/SSD-1B/blob/main/unet/diffusion_pytorch_model.fp16.safetensors

    # only support huggingface model hub
    pattern = r"https://huggingface\.co/([^/]+)/([^/]+)/blob/main/(.+)"
    match = re.search(pattern, model_url)    
    if match:
        org = match.group(1)
        repoid = match.group(2)
        subfolder = match.group(3).rstrip('/')  # 去除末尾的斜杠
        subfolder_parts = subfolder.split('/')
        filename = subfolder_parts[-1]
        subfolder_path = '/'.join(subfolder_parts[:-1])
        save_model_name = f"{org}_{repoid}_{subfolder_path}_{filename}".replace('/', '_')
        return {
            "org": org,
            "repoid": repoid,
            "subfolder": subfolder_path,
            "filename": filename,
            "save_path": save_path,
            "save_name": save_model_name
        }


logger.info("Loading publish page")
page.page_init()

with st.container():
    with page.stylable_button_container():
        header_row = row([0.85, 0.15], vertical_align="top")
        header_row.title("✈️ Publish and share to friends")
        back_button = header_row.button("Back Workspace", help="Back to your workspace", key='publish_back_workspace')
        if back_button:
            switch_page("Workspace")

    
    apps = get_sqlite_instance().get_all_apps()
    app_name_map = {app['name']: app for app in apps if app['status'] == AppStatus.PREVIEWED.value} 
    preview_app_opts = list(app_name_map.keys())
    if len(preview_app_opts) == 0:
        st.warning("No app is available to publish, please preview app first.")
        st.stop()
    else:
        with st.container():

            st.selectbox("My Apps", options=preview_app_opts, key='publish_select_app', help="Select a app to publish.")

            app = app_name_map[st.session_state['publish_select_app']]
            app_name = app['name']
            api_data_json = json.loads(app['api_conf'])
            app_data_json = json.loads(app['app_conf'])

            # config app nodes
            with open('public/comfyui/object_info.json', 'r') as f:
                object_info = json.load(f)
                with st.expander("Parse comfyui node info", expanded=True):
                    for node_id in api_data_json:
                        inputs = api_data_json[node_id]['inputs']
                        class_type = api_data_json[node_id]['class_type']
                        if class_type in object_info:
                            st.write(f":green[Check node info\, {node_id}\:{class_type}]")
                        else:
                            st.write(f":red[Node info not found\, {node_id}\:{class_type}]")
                            st.session_state['publish_invalid_node'] = True

            # load comfyui/object_model from json
            with open('public/comfyui/object_model.json', 'r') as f:
                object_model = json.load(f)

                # config app models
                with st.expander("Config app models", expanded=True):
                    for node_id in api_data_json:
                        inputs = api_data_json[node_id]['inputs']
                        class_type = api_data_json[node_id]['class_type']
                        if class_type in object_model:
                            model_name_path = object_model[class_type]
                            input_model_row = row([0.5, 0.5])
                            for param in inputs:
                                if param in model_name_path:
                                    model_input_name = f"{node_id}:{class_type}:{inputs[param]}"
                                    input_model_row.text_input("App model name", value=model_input_name, help="App model name")
                                    input_model_row.text_input("Input model url", key=model_input_name, help="Input model url of huggingface model hub")
                                                        
            
            publish_button = st.button("Publish", key='publish_button', type='primary', 
                      help="Publish app to store and share with your friends")
            if publish_button:
                if 'publish_invalid_node' in st.session_state:
                    st.warning("Invalid node, please check node info.")
                else:
                    # check model url
                    models = {}
                    for node_id in api_data_json:
                        inputs = api_data_json[node_id]['inputs']
                        class_type = api_data_json[node_id]['class_type']
                        if class_type in object_model:
                            model_name_path = object_model[class_type]
                            for param in inputs:
                                if param in model_name_path:
                                    model_path = model_name_path[param]
                                    model_input_name = f"{node_id}:{class_type}:{inputs[param]}"
                                    if not st.session_state[model_input_name]:
                                        st.warning(f"Please input model url for {model_input_name}")
                                        st.stop()
                                    else:
                                        model_url = st.session_state[model_input_name]
                                        model = parsed_model_url(model_url, model_path)
                                        if model:
                                            inputs[param] = model['save_name']
                                            
                                            models[model_input_name] = model
                                        else:
                                            st.warning(f"Invalid model url for {model_input_name}")
                                            st.stop()
                            
                    
                    # update app_conf and status
                    app_data_json['models'] = models
                    app_data = json.dumps(app_data_json)
                    logger.info(f"update models, {app_data_json} {api_data_json}")
                    # get_sqlite_instance().update_app_publish(app_name, app_data)

                    # call api to publish app

                    
                    st.success("Publish success!")
                    st.stop()
