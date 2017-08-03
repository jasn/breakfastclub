import json
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://breakfast:monster@localhost/breakfastclub'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = '13'

# read email config
this_directory = os.path.dirname(__file__)
email_config_path = os.path.join(this_directory, 'email_config.json')
with open(email_config_path) as email_config_file:
    app.config.update(json.load(email_config_file))
app.config['EMAIL_REMINDER_SENDER'] = 'breakfastclub@example.com'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
csrf = CSRFProtect(app)
mail = Mail(app)

from . import models
from . import views
from . import admin
from . import commands


@login_manager.user_loader
def load_user(person_id):
    return db.session.query(models.Person).get(person_id)
