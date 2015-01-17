from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

# make debug and error logging easier
debug = app.logger.debug
error = app.logger.error

from api.mod_api.views import mod_api as api_module
app.register_blueprint(api_module)

from api import views


