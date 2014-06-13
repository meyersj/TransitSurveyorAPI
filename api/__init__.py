from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import logging
import os

KEYS = "keys"

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

app.debug = True

app.config[KEYS] = os.path.abspath(os.path.join(os.getcwd(), '../keys'))

#handler = logging.FileHandler('/tmp/app.log')
#handler.setLevel(logging.DEBUG)
#app.logger.addHandler(handler)

from api import models, views

