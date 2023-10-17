import os
import json
from loguru import logger
import streamlit as st
import module.utils as utils

"""
comfyflow_apps table
id INTEGER
name TEXT
description TEXT
image BLOB
app_conf TEXT
api_conf TEXT
preview_image BLOB
template TEXT
url TEXT
status TEXT
created_at NUMERIC
updated_at NUMERIC
"""

class SQLiteHelper:
    def __init__(self) -> None:
        self.db_conn = st.experimental_connection('comfyflow_db', type='sql')
        self.app_talbe_name = 'comfyflow_apps'
        logger.info(f"db_conn: {self.db_conn}, app_talbe_name: {self.app_talbe_name}")

        # Create a table if it doesn't exist.
        self._init_table()

        # load default apps
        self._init_load_apps()

    @property
    def session(self):
        return self.db_conn.session
    
    def _init_table(self):
        with self.session as s:
            logger.info(f"init table: {self.app_talbe_name}")
            sql = f'CREATE TABLE IF NOT EXISTS {self.app_talbe_name} (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, image BLOB, app_conf TEXT, api_conf TEXT, preview_image BLOB, template TEXT, url TEXT, status TEXT, created_at NUMERIC, updated_at NUMERIC);'
            s.execute(sql)

            # create index on name
            sql = f'CREATE INDEX IF NOT EXISTS {self.app_talbe_name}_name_index ON {self.app_talbe_name} (name);'
            s.execute(sql)
            s.commit()

    def _init_load_apps(self):
        # Insert some data with conn.session.
        with self.session as s:
            app_dirs = utils.listdirs('workflows')
            if len(app_dirs) == 0:
                logger.info(f"no apps found in workflows")
                return
            logger.info(f"init workflows, {app_dirs}")
            for app_dir in app_dirs:
                try:
                    app = {}
                    app_conf = f"workflows/{app_dir}/app.json"
                    with open(app_conf, 'r') as f:
                        app_json = json.load(f)
                        app['name'] = app_json['name']
                        app['description'] = app_json['description']
                        app['app_conf'] = json.dumps(app_json)
                    
                    # check if app exists
                    sql = f'SELECT * FROM {self.app_talbe_name} WHERE name=:name;'
                    ret = s.execute(sql, {'name': app['name']}).fetchone()
                    if ret is not None:
                        logger.info(f"app {app_dir} exists, skip")
                        continue
                    else:
                        logger.info(f"app {app_dir} not exists, insert {app}")
                        
                        # load api_conf
                        api_conf = f"workflows/{app_dir}/prompt.json"
                        with open(api_conf, 'r') as f:
                            api_json = json.load(f)
                            app['api_conf'] = json.dumps(api_json)
                        
                        image = f"workflows/{app_dir}/app.png"
                        if os.path.exists(image):
                            # update image
                            app['image'] = open(image, 'rb').read()
                        else:
                            app['image'] = None

                        sql = f'INSERT INTO {self.app_talbe_name} (name, description, image, app_conf, api_conf) VALUES (:name, :description, :image, :app_conf, :api_conf);'
                        s.execute(sql, app)
                except Exception as e:
                    logger.error(f"load app {app_dir} failed, {e}")
            s.commit()

    def get_apps(self):
        with self.session as s:
            sql = f'SELECT * FROM {self.app_talbe_name};'
            apps = s.execute(sql).fetchall()
            return apps
        
    def insert_app(self, app):
        with self.session as s:
            logger.info(f"insert app: {app}")
            app['app_conf'] = open(app['app_conf'], 'r').read()
            app['api_conf'] = open(app['api_conf'], 'r').read()
            app['image'] = open(app['image'], 'rb').read()
            sql = f'INSERT INTO {self.app_talbe_name} (name, description, image, app_conf, api_conf) VALUES (:name, :description, :image, :app_conf, :api_conf);'
            s.execute(sql, app)
            s.commit()

    def update_app(self, app):
        with self.session as s:
            logger.info(f"update app: {app}")
            app['app_conf'] = open(app['app_conf'], 'r').read()
            app['api_conf'] = open(app['api_conf'], 'r').read()
            app['image'] = open(app['image'], 'rb').read()
            sql = f'UPDATE {self.app_talbe_name} SET name=:name, description=:description, image=:image, app_conf=:app_conf, api_conf=:api_conf WHERE id=:id;'
            s.execute(sql, app)
            s.commit()