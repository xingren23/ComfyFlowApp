from loguru import logger
import streamlit as st
from sqlalchemy import text
from enum import Enum

"""
comfyflow_apps table
    id INTEGER
    name TEXT
    description TEXT
    image BLOB
    app_conf TEXT
    api_conf TEXT
    template TEXT
    status TEXT
    created_at TEXT
    updated_at TEXT
"""
# enum app status
class AppStatus(Enum):
    PUBLISHED = "Published"
    DOWNLOADING = "Downloading"
    DOWNLOADED = "Downloaded"
    INSTALLING = "Installing"
    INSTALLED = "Installed"
    ERROR = "Error"


class SQLiteHelper:
    def __init__(self) -> None:
        self.db_conn = st.experimental_connection('comfyflow_db', type='sql')
        self.app_talbe_name = 'comfyflow_apps'
        self._init_table()
        logger.info(f"db_conn: {self.db_conn}, app_talbe_name: {self.app_talbe_name}")

    @property
    def session(self):
        return self.db_conn.session
    
    def _init_table(self):
        # Create a table if it doesn't exist.
        with self.session as s:
            sql = text(f'CREATE TABLE IF NOT EXISTS {self.app_talbe_name} (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, image BLOB, app_conf TEXT, api_conf TEXT, template TEXT, url TEXT, status TEXT, created_at TEXT, updated_at TEXT);')
            s.execute(sql)

            # create index on name
            sql = text(f'CREATE INDEX IF NOT EXISTS {self.app_talbe_name}_name_index ON {self.app_talbe_name} (name);')
            s.execute(sql)
            s.commit()
            logger.info(f"init app table {self.app_talbe_name} and index")

    def get_all_apps(self):
        with self.session as s:
            logger.info("get apps from db")
            sql = text(f'SELECT id, name, description, image, app_conf, api_conf, template, url, status FROM {self.app_talbe_name} order by id;')
            apps = s.execute(sql).fetchall()
            return apps
        
    def get_my_apps(self):
        # get installed apps
        with self.session as s:
            logger.info("get my apps from db")
            sql = text(f'SELECT id, name, description, image, app_conf, api_conf, template, url, status FROM {self.app_talbe_name} WHERE status=:status order by id;')
            apps = s.execute(sql, {'status': AppStatus.INSTALLED.value}).fetchall()
            return apps

    def get_app(self, name):
        with self.session as s:
            logger.info(f"get app by name: {name}")
            sql = text(f'SELECT * FROM {self.app_talbe_name} WHERE name=:name;')
            app = s.execute(sql, {'name': name}).fetchone()
            return app
        
    def get_app_by_id(self, id):
        with self.session as s:
            logger.info(f"get app by id: {id}")
            sql = text(f'SELECT * FROM {self.app_talbe_name} WHERE id=:id;')
            app = s.execute(sql, {'id': id}).fetchone()
            return app
        
    def delete_app(self, name):
        with self.session as s:
            logger.info(f"delete app: {name}")
            sql = text(f'DELETE FROM {self.app_talbe_name} WHERE name=:name;')
            s.execute(sql, dict(name=name))
            s.commit()

    def update_app_status(self, id, status):
        with self.session as s:
            logger.info(f"update app status: {id}, {status}")
            sql = text(f'UPDATE {self.app_talbe_name} SET status=:status WHERE id=:id;')
            s.execute(sql, dict(id=id, status=status))
            s.commit()

    def update_api_conf(self, id, api_conf):
        with self.session as s:
            logger.info(f"update app api_conf: {id}, {api_conf}")
            sql = text(f'UPDATE {self.app_talbe_name} SET api_conf=:api_conf WHERE id=:id;')
            s.execute(sql, dict(id=id, api_conf=api_conf))
            s.commit()

       