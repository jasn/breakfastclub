import click
import datetime
from random import shuffle

from flask_login import UserMixin, AnonymousUserMixin

from breakfastclub import app, db, migrate, login_manager

class Person(db.Model, UserMixin):
    __tablename__ = 'person'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(191), nullable=False)  # varchar max length utf8mb4
    active = db.Column(db.Boolean, default=True, nullable=False)
    token = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return '<Person(name=%s, email=%s)>' % (self.name, self.email)

class BreadList(db.Model):
    __tablename__ = 'breadlist'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    person_id = db.Column(db.Integer,
                          db.ForeignKey(Person.id, name='fk_breadlist_person_id'),
                          nullable=False)


@app.cli.command('generate-breadlist')
@click.option('--day', default=1)
# 1 is tuesday, following python date.weekday()
def generate_breadlist(day):
    """
    Generates a new breadlist.
    """
    active_people = db.session.query(Person).filter_by(active=True).all()
    shuffle(active_people)
    today = datetime.date.today()

    week_length = 7
    if today.weekday() >= day:
        # next week has next breakfast day.

        days_to_add = week_length - (today.weekday() - day)
        pass
    else:
        # this week has next breakfast day.
        days_to_add = day - today.weekday()
    next_breakfast_date = (datetime.date.today() +
                           datetime.timedelta(days=days_to_add))
    breakfast_dates = [(next_breakfast_date +
                        datetime.timedelta(week_length * i))
                       for i, _ in enumerate(active_people)]


    for person, date in zip(active_people, breakfast_dates):
        print("[%s] %s (%s)" % (date, person.name, person.email))
