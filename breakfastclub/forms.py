import json
import datetime
from datetime import timedelta

from wtforms import StringField, validators, widgets
from flask_wtf import FlaskForm
from wtforms.widgets.html5 import EmailInput
from breakfastclub.models import Person

from breakfastclub import db

class AddPersonForm(FlaskForm):

    name = StringField(
        'name',
        [validators.Length(max=Person.name.property.columns[0].type.length),
         validators.InputRequired()],
    )
    email = StringField(
        'email',
        [validators.Length(max=Person.email.property.columns[0].type.length),
         validators.Email(),
         validators.InputRequired()],
        widget=EmailInput(),
    )

class ShowLoginForm(FlaskForm):
    token = StringField('token', [validators.InputRequired()])

    def validate(self):
        if not super().validate():
            return False
        token = self.token.data
        person = db.session.query(Person).filter_by(token=token).first()
        if person is None:
            self.token.errors.append('Invalid token.')
            return False

        self.person = person
        return True
