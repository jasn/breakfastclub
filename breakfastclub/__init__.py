from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://breakfast:monster@localhost/breakfastclub'
app.secret_key = '13'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
csrf = CSRFProtect(app)

from . import models
from . import views

@login_manager.user_loader
def load_user(person_id):
    return db.session.query(models.Person).get(person_id)
