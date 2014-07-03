from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import logging
import os
import getpass

KEYS = 'keys'
USER = 'ubuntu'
KEYS_PATH = 'api/keys'

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

#modifed to False if deploying with wsgi
app.debug = True
app.config[KEYS] = os.path.join('home', USER, KEYS_PATH)

from api import models, views
