from wtforms import Form, StringField, validators, widgets
from wtforms.widgets.html5 import EmailInput
from breakfastclub.models import Person

from breakfastclub import db

class AddPersonForm(Form):

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

class ShowLoginForm(Form):
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
