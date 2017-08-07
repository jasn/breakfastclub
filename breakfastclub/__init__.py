import json
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail


app = Flask(__name__)

this_directory = os.path.dirname(__file__)
config_path = os.path.join(this_directory,
                           os.environ.get('BREAKFASTCLUB_CONFIG',
                                          'config.json'))
config_secret_path = os.path.join(this_directory,
                                  os.environ.get('BREAKFASTCLUB_CONFIG_SECRET',
                                                 'config_secret.json'))
with open(config_path) as config_file:
    app.config.update(json.load(config_file))
with open(config_secret_path) as config_file:
    app.config.update(json.load(config_file))
    app.secret_key = app.config['SECRET_KEY']

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
csrf = CSRFProtect(app)
mail = Mail(app)

from . import models  # noqa
from . import views   # noqa
from . import admin   # noqa
from . import commands  # noqa


@login_manager.user_loader
def load_user(person_id):
    return db.session.query(models.Person).get(person_id)
