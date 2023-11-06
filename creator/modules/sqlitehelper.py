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
    preview_image BLOB
    template TEXT
    url TEXT
    status TEXT
    created_at TEXT
    updated_at TEXT
"""
# enum app status
class AppStatus(Enum):
    CREATED = "Created"
    PREVIEWED = "Previewed"
    PUBLISHED = "Published"
    RUNNING = "Running"
    STARTED = "Started"
    STOPPING = "Stopping"
    STOPPED = "Stopped"


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
        
    def create_app(self, app):
        with self.session as s:
            app['status'] = AppStatus.CREATED.value
            logger.info(f"insert app: {app['name']} {app['description']}")
            sql = text(f'INSERT INTO {self.app_talbe_name} (name, description, image, template, app_conf, api_conf, status, created_at) VALUES (:name, :description, :image, :template, :app_conf, :api_conf, :status, datetime("now"));')
            s.execute(sql, app)
            s.commit()

    def edit_app(self, id, name, description, app_conf):
        # update name, description, app_conf, could not update image, api_conf
        with self.session as s:
            logger.info(f"update app conf: {id} {name} {description} {app_conf}")
            sql = text(f'UPDATE {self.app_talbe_name} SET name=:name, description=:description, app_conf=:app_conf, updated_at=datetime("now") WHERE id=:id;')
            s.execute(sql, dict(id=id, name=name, description=description, app_conf=app_conf))
            s.commit()

    def update_app_preview(self, name):
        # update preview_image
        with self.session as s:
            logger.info(f"update app preview: {name}")
            sql = text(f'UPDATE {self.app_talbe_name} SET status=:status, updated_at=datetime("now") WHERE name=:name;')
            s.execute(sql, dict(status=AppStatus.PREVIEWED.value, name=name))
            s.commit()
    
    def update_app_publish(self, name, app_conf):
        # update publish
        with self.session as s:
            logger.info(f"update app publish: {name} {app_conf}")
            sql = text(f'UPDATE {self.app_talbe_name} SET app_conf=:app_conf, status=:status, updated_at=datetime("now") WHERE name=:name;')
            s.execute(sql, dict(app_conf=app_conf, status=AppStatus.PUBLISHED.value, name=name))
            s.commit()

    def delete_app(self, name):
        with self.session as s:
            logger.info(f"delete app: {name}")
            sql = text(f'DELETE FROM {self.app_talbe_name} WHERE name=:name;')
            s.execute(sql, dict(name=name))
            s.commit()

    def update_app_url(self, name, url):
        with self.session as s:
            logger.info(f"update app url: {name} {url}")
            sql = text(f'UPDATE {self.app_talbe_name} SET url=:url, updated_at=datetime("now") WHERE name=:name;')
            s.execute(sql, dict(url=url, name=name))
            s.commit()      