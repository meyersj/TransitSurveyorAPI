from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import logging

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

handler = logging.FileHandler('/tmp/app.log')
handler.setLevel(logging.DEBUG)
app.logger.addHandler(handler)

from api import models, views

