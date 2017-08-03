import json
import datetime
from datetime import timedelta
from random import shuffle

from wtforms import HiddenField, StringField, validators, widgets
from wtforms.fields import FieldList, FormField, BooleanField

from flask_wtf import FlaskForm

from wtforms.widgets.html5 import EmailInput
from wtforms.widgets import HiddenInput
from breakfastclub.models import Person, BreadList

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
        person = db.session.query(Person).filter_by(token=token).scalar()
        if person is None:
            self.token.errors.append('Invalid token.')
            return False

        self.person = person
        return True

class GenerateBreadListForm(FlaskForm):

    data = StringField('data', widget=HiddenInput())

    def validate(self):
        if not super().validate():
            return False

        try:
            parsed_data = json.loads(self.data.data)
        except ValueError:
            self.data.errors.append('Invalid JSON.')
            return False

        # verify all dates greater than max date in DB.
        # verify all persons exist and active in DB.
        person_ids = [d['person_id'] for d in parsed_data]
        if len(person_ids) != len(set(person_ids)):
            self.data.errors.append('Duplicate person.')
            return False
        people = list(db.session.query(Person).filter(Person.id.in_(person_ids),
                                                      Person.active == True))
        if len(people) != len(person_ids):
            self.data.errors.append('Inactive person or invalid person.')
            return False

        dates = [datetime.datetime.strptime(d['date'], '%Y-%m-%d').date()
                 for d in parsed_data]

        qs = db.session.query(BreadList)
        qs = qs.order_by(BreadList.date.desc())
        max_date = qs.first().date
        if not all(date > max_date for date in dates):
            self.data.errors.append('Invalid date.')
            return False

        self.new_breadlist = [BreadList(person_id=p, date=d)
                              for p, d in zip(person_ids, dates)]
        return True

    def save(self):
        db.session.add_all(self.new_breadlist)
        db.session.commit()

    def __init__(self, *args, **kwargs):

        def find_next_tuesday(date):
            to_add = timedelta(days=(0 - date.weekday()) % 7 + 1)
            return date + to_add

        super().__init__(*args, **kwargs)
        people = db.session.query(Person).filter(Person.active==True).all()
        qs = db.session.query(BreadList)
        qs = qs.order_by(BreadList.date.desc())
        max_date = qs.first()
        today = datetime.date.today()
        basis = max(max_date.date, today) if max_date else today
        next_tuesday = find_next_tuesday(basis)
        to_add = timedelta(days=7)
        self.new_bringers = []
        for person in people:
            self.new_bringers.append(dict(person=person, person_id=person.id, date=next_tuesday))
            next_tuesday += to_add
        shuffle(self.new_bringers)
        self.data.default = json.dumps(
            [{'person_id': b['person_id'], 'date': b['date'].strftime('%Y-%m-%d')}
             for b in self.new_bringers]
        )
        self.process()

class TokenManagementSubForm(FlaskForm):
    person_id = StringField('id', widget=HiddenInput())  # id is being shadowed
    person_name = StringField('name', validators=[validators.InputRequired()])  # name is being shadowed
    email = StringField('email', validators=[validators.InputRequired()])
    token_link = StringField('token_link')
    generate_token = BooleanField('generate_token')
    email_token = BooleanField('email_token')

    # def process(self, formdata=None, obj=None, **kwargs):
    #     super().process(formdata, obj, kwargs)
    #     self.id.default = kwargs['id']
    #     self.name.default = kwargs['name']
    #     self.email.default = kwargs['email']
    #     self.token_link.default = kwargs['token_link']

    #     self.id.process(formdata)
    #     self.name.process(formdata)
    #     self.email.process(formdata)
    #     self.token_link.process(formdata)

class TokenManagementFormBase(FlaskForm):

    keys = ['person_name', 'email', 'token_link',
            'generate_token', 'email_token']

    def rows(self):
        for person in self.persons:
            yield {k: getattr(self, k + '_' + str(person.id))
                   for k in self.keys}

    def validate(self):
        if not super().validate():
            return False

        for person in self.persons:
            person_changed = False
            person.name = getattr(self, 'person_name_' + str(person.id)).data
        db.session.commit()
        return True


def get_token_management_form(persons):

    fields = {}
    for person in persons:
        fields['person_name_' + str(person.id)] = StringField(
            default=person.name,
            validators=[validators.InputRequired()],
        )
        fields['email_' + str(person.id)] = StringField(
            default=person.email,
            validators=[validators.InputRequired()],
        )
        fields['token_link_' + str(person.id)] = StringField(default=person.token)
        fields['generate_token_' + str(person.id)] = BooleanField(default=False)
        fields['email_token_' + str(person.id)] = BooleanField(default=False)

    TokenManagementForm = type('TokenManagementForm',
                               (TokenManagementFormBase,),
                               fields)
    TokenManagementForm.persons = persons
    return TokenManagementForm


class TokenManagementForm(FlaskForm):
    rows = FieldList(FormField(TokenManagementSubForm, separator='_'))
