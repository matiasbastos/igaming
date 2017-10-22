from flask import Flask
from flask_appbuilder import AppBuilder
from flask_appbuilder.security.mongoengine.manager import SecurityManager
from flask_mongoengine import MongoEngine
from mongoengine.connection import connect, disconnect


def app_factory(**config_overrides):
    app = Flask(__name__, static_folder='static', static_url_path='')
    # Load config.
    app.config.from_object('config')
    # apply overrides
    app.config.update(config_overrides)
    # Setup the database.
    db = MongoEngine(app)
    return app, db


def create_app():
    return app_factory(
        MONGODB_SETTINGS={'DB': 'testing'},
        TESTING=True,
        CSRF_ENABLED=False,
    )


def create_user(app):
    appbuilder = AppBuilder(app, security_manager_class=SecurityManager)
    appbuilder.sm.create_db()
    role_admin = appbuilder.sm.find_role(appbuilder.sm.auth_role_admin)
    user = appbuilder.sm.add_user('test_user',
                                  'test',
                                  'user',
                                  'test@user.com',
                                  role_admin,
                                  'test_user')
    return user


def drop_db():
    conn = connect()
    conn.drop_database('testing')
    disconnect()
