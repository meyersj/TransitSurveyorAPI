from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

#modifed to False if deploying with wsgi
app.debug = True

from api.mod_api.views import mod_api as api_module
from api.mod_onoff.views import mod_onoff as onoff_module
#from api.mod_long.views import mod_long as long_module

app.register_blueprint(api_module)
app.register_blueprint(onoff_module)
#app.register_blueprint(long_module)

Bootstrap(app)

from api import views


