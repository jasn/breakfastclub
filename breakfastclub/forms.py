from wtforms import Form, StringField, validators, widgets
from wtforms.widgets.html5 import EmailInput
from breakfastclub.models import Person

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

