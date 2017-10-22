import logging
from flask import Flask
from flask_appbuilder import AppBuilder
from flask_mongoengine import MongoEngine
from flask_appbuilder.security.mongoengine.manager import SecurityManager

"""
App def
"""
app = Flask(__name__)
app.config.from_object('config')
db = MongoEngine(app)
appbuilder = AppBuilder(app, security_manager_class=SecurityManager)
