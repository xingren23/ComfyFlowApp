from loguru import logger
import base64
import streamlit as st
from sqlalchemy import text
from modules import AppStatus

"""
my_apps table
    id TEXT
    name TEXT
    description TEXT
    image TEXT
    app_conf TEXT
    api_conf TEXT
    template TEXT
    status TEXT
    created_at TEXT
    updated_at TEXT
"""

class MyAppModel:
    def __init__(self) -> None:
        self.db_conn = st.connection('comfyflow_db', type='sql')
        self.app_table_name = 'my_apps'
        self._init_table()
        logger.debug(f"db_conn: {self.db_conn}, app_table_name: {self.app_table_name}")

    @property
    def session(self):
        return self.db_conn.session
    
    def _init_table(self):
        # Create a table if it doesn't exist.
        with self.session as s:
            sql = text(f'CREATE TABLE IF NOT EXISTS {self.app_table_name} (id TEXT PRIMARY KEY, name TEXT, description TEXT, image TEXT, app_conf TEXT, api_conf TEXT, template TEXT, url TEXT, status TEXT, created_at TEXT, updated_at TEXT);')
            s.execute(sql)

            # create index on name
            sql = text(f'CREATE INDEX IF NOT EXISTS {self.app_table_name}_name_index ON {self.app_table_name} (name);')
            s.execute(sql)
            s.commit()
            logger.info(f"init app table {self.app_table_name} and index")

    def sync_apps(self, apps):
        
        with self.session as s:
            # reset local apps
            sql = text(f'SELECT id, status FROM {self.app_table_name} where status!=:status order by id;')
            local_apps = s.execute(sql, dict(status=AppStatus.INSTALLED.value)).fetchall()
            delete_apps = []
            for app in local_apps:
                delete_apps.append(app.id)
                self.delete_app_by_id(app.id)
            logger.info(f"reset local apps, {delete_apps}")

        # sync apps from comfyflow.app
        with self.session as s:
            sql = text(f'SELECT id, status FROM {self.app_table_name} order by id;')
            local_apps = s.execute(sql).fetchall()
            local_app_ids = {app.id: app for app in local_apps}
            sync_apps = []
            for app in apps:
                # convert base64 image to bytes
                base64_data = app['image'].split(',')[-1]
                image_bytes = base64.b64decode(base64_data)

                if app['id'] in local_app_ids:
                    if local_app_ids[app['id']].status == AppStatus.PUBLISHED.value:
                        # update app
                        sql = text(f'UPDATE {self.app_table_name} SET name=:name, description=:description, image=:image, template=:template, status=:status, updated_at=datetime("now") WHERE id=:id;')
                        s.execute(sql, dict(id=app['id'], name=app['name'], description=app['description'], image=image_bytes, template=app['template'], status=AppStatus.PUBLISHED.value))
                        s.commit()
                        sync_apps.append(app['name'])
                        logger.info(f"update app {app['name']} to my apps")
                else:
                    # insert app
                    sql = text(f'INSERT INTO {self.app_table_name} (id, name, description, image, template, status, created_at, updated_at) VALUES (:id, :name, :description, :image, :template, :status, datetime("now"), datetime("now") );')
                    s.execute(sql, dict(id=app['id'], name=app['name'], description=app['description'], image=image_bytes, template=app['template'], status=AppStatus.PUBLISHED.value))
                    s.commit()
                    sync_apps.append(app['name'])
                    logger.info(f"insert app {app['name']} my apps")
            logger.info(f"sync apps from comfyflow.app, {sync_apps}")
            return sync_apps

    def get_all_apps(self):
        with self.session as s:
            logger.info("get apps from db")
            sql = text(f'SELECT id, name, description, image, app_conf, api_conf, endpoint, template, url, status, username FROM {self.app_table_name} order by id desc;')
            apps = s.execute(sql).fetchall()
            return apps
        
    def get_my_installed_apps(self):
        # get installed apps
        with self.session as s:
            logger.debug("get my apps from db")
            sql = text(f'SELECT id, name, description, image, app_conf, api_conf, template, url, status, username FROM {self.app_table_name} WHERE status=:status order by id desc;')
            apps = s.execute(sql, {'status': AppStatus.INSTALLED.value}).fetchall()
            return apps

    def get_app(self, name):
        with self.session as s:
            logger.debug(f"get app by name: {name}")
            sql = text(f'SELECT * FROM {self.app_table_name} WHERE name=:name;')
            app = s.execute(sql, {'name': name}).fetchone()
            return app
        
    def get_app_by_id(self, id):
        with self.session as s:
            logger.debug(f"get app by id: {id}")
            sql = text(f'SELECT * FROM {self.app_table_name} WHERE id=:id;')
            app = s.execute(sql, {'id': id}).fetchone()
            return app
        
    def delete_app(self, name):
        with self.session as s:
            logger.info(f"delete app: {name}")
            sql = text(f'DELETE FROM {self.app_table_name} WHERE name=:name;')
            s.execute(sql, dict(name=name))
            s.commit()

    def delete_app_by_id(self, id):
        with self.session as s:
            logger.info(f"delete app: {id}")
            sql = text(f'DELETE FROM {self.app_table_name} WHERE id=:id;')
            s.execute(sql, dict(id=id))
            s.commit()

    def update_app_status(self, id, status):
        with self.session as s:
            logger.info(f"update app status: {id}, {status}")
            sql = text(f'UPDATE {self.app_table_name} SET status=:status WHERE id=:id;')
            s.execute(sql, dict(id=id, status=status))
            s.commit()

    def update_api_conf(self, id, api_conf):
        with self.session as s:
            logger.info(f"update app api_conf: {id}, {api_conf}")
            sql = text(f'UPDATE {self.app_table_name} SET api_conf=:api_conf WHERE id=:id;')
            s.execute(sql, dict(id=id, api_conf=api_conf))
            s.commit()

    def update_app_conf(self, id, app_conf):
        with self.session as s:
            logger.info(f"update app app_conf: {id}, {app_conf}")
            sql = text(f'UPDATE {self.app_table_name} SET app_conf=:app_conf WHERE id=:id;')
            s.execute(sql, dict(id=id, app_conf=app_conf))
            s.commit()

       