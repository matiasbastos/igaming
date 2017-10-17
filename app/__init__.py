import logging
from flask import Flask
from flask_appbuilder.security.mongoengine.manager import SecurityManager
from flask_appbuilder import AppBuilder
from flask_mongoengine import MongoEngine
from app.index_view import Index

"""
Logging configuration
"""
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)

"""
App def
"""
app = Flask(__name__)
app.config.from_object('config')
db = MongoEngine(app)
appbuilder = AppBuilder(app,
                        security_manager_class=SecurityManager,
                        indexview=Index)
from app import views
