from loguru import logger
import streamlit as st
from sqlalchemy import text
from modules import AppStatus

"""
comfyflow_apps table
    id INTEGER
    name TEXT
    description TEXT
    image TEXT
    app_conf TEXT
    api_conf TEXT
    template TEXT
    url TEXT
    status TEXT
    created_at TEXT
    updated_at TEXT
"""

class WorkspaceModel:
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
            sql = text(f'CREATE TABLE IF NOT EXISTS {self.app_talbe_name} (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, image TEXT, app_conf TEXT, api_conf TEXT, template TEXT, url TEXT, status TEXT, created_at TEXT, updated_at TEXT);')
            s.execute(sql)

            # alert table: add username column
            try:
                s.execute(f'ALTER TABLE {self.app_talbe_name} ADD COLUMN username TEXT;' )
            except:
                columns = s.execute("PRAGMA table_info(asin)").fetchall()
                logger.info(f"{self.app_talbe_name} columns: {columns}")
            # alert table: add workflow_conf column
            try:
                s.execute(f'ALTER TABLE {self.app_talbe_name} ADD COLUMN workflow_conf TEXT;' )
            except:
                columns = s.execute("PRAGMA table_info(asin)").fetchall()
                logger.info(f"{self.app_talbe_name} columns: {columns}")
            

            # create index on name
            sql = text(f'CREATE INDEX IF NOT EXISTS {self.app_talbe_name}_name_index ON {self.app_talbe_name} (name);')
            s.execute(sql)

            s.commit()
            logger.info(f"init app table {self.app_talbe_name} and index")

    def get_all_apps(self):
        with self.session as s:
            logger.info("get apps from db")
            sql = text(f'SELECT id, name, description, image, app_conf, api_conf, workflow_conf, template, url, status, username FROM {self.app_talbe_name} order by id desc;')
            apps = s.execute(sql).fetchall()
            return apps
        
    def get_installed_apps(self):
        with self.session as s:
            logger.info("get installed apps from db")
            sql = text(f'SELECT id, name, description, image, app_conf, api_conf, workflow_conf, template, url, status, username FROM {self.app_talbe_name} WHERE status=:status order by id desc;')
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
        
    def create_app(self, app):
        with self.session as s:
            app['status'] = AppStatus.CREATED.value
            logger.info(f"insert app: {app['name']} {app['description']}")
            username = st.session_state.get('username', 'anonymous')
            app['username'] = username
            sql = text(f'INSERT INTO {self.app_talbe_name} (username, name, description, image, template, app_conf, api_conf, workflow_conf, status, created_at) VALUES (:username, :name, :description, :image, :template, :app_conf, :api_conf, :workflow_conf, :status, datetime("now"));')
            s.execute(sql, app)
            s.commit()

    def edit_app(self, id, name, description, app_conf):
        # update name, description, app_conf, could not update image, api_conf
        with self.session as s:
            logger.info(f"update app conf: {id} {name} {description} {app_conf}")
            username = st.session_state.get('username', 'anonymous')
            sql = text(f'UPDATE {self.app_talbe_name} SET username=:username, name=:name, description=:description, app_conf=:app_conf, updated_at=datetime("now") WHERE id=:id;')
            s.execute(sql, dict(id=id, username=username, name=name, description=description, app_conf=app_conf))
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

    def update_app_install(self, name):
        # update install
        with self.session as s:
            logger.info(f"update app install: {name}")
            sql = text(f'UPDATE {self.app_talbe_name} SET status=:status, updated_at=datetime("now") WHERE name=:name;')
            s.execute(sql, dict(status=AppStatus.INSTALLED.value, name=name))
            s.commit()

    def update_app_uninstall(self, name):
        # update uninstall
        with self.session as s:
            logger.info(f"update app uninstall: {name}")
            sql = text(f'UPDATE {self.app_talbe_name} SET status=:status, updated_at=datetime("now") WHERE name=:name;')
            s.execute(sql, dict(status=AppStatus.UNINSTALLED.value, name=name))
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