import json
import datetime
from datetime import timedelta
from random import shuffle

from wtforms import StringField, validators, widgets
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
        person = db.session.query(Person).filter_by(token=token).first()
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
            self.new_bringers.append(BreadList(person=person, person_id=person.id, date=next_tuesday))
            next_tuesday += to_add
        shuffle(self.new_bringers)
        self.data.default = json.dumps(
            [{'person_id': b.person_id, 'date': b.date.strftime('%Y-%m-%d')}
             for b in self.new_bringers]
        )
        self.process()
        db.session.rollback()
