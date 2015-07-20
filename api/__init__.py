# Copyright © 2015 Jeffrey Meyers
# This program is released under the "MIT License".
# Please see the file COPYING in the source
# distribution of this software for license terms.

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


