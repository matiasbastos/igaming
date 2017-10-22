import logging
from flask import Flask
from flask_appbuilder import AppBuilder
from flask_mongoengine import MongoEngine
from auth_manager import CustomSecurityManager
from index_view import Index

"""
Logging configuration
"""
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s')
logging.getLogger().setLevel(logging.INFO)

"""
App def
"""
app = Flask(__name__)
app.config.from_object('config')
db = MongoEngine(app)
appbuilder = AppBuilder(app,
                        security_manager_class=CustomSecurityManager,
                        indexview=Index)
from . import views
