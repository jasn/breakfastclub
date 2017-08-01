from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://breakfast:monster@localhost/breakfastclub'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from . import models
from . import views

