import click
import datetime
from random import shuffle

from breakfastclub import app, db, migrate

class Person(db.Model):
    __tablename__ = 'person'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(191))  # varchar max length utf8mb4
    active = db.Column(db.Boolean)
    def __repr__(self):
        return '<Person(name=%s, email=%s)>' % (self.name, self.email)


class BreadList(db.Model):
    __tablename__ = 'breadlist'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    person_id = db.Column(db.Integer, db.ForeignKey(Person.id))


@app.cli.command('generate-breadlist')
@click.option('--day', default=1)
# 1 is tuesday, following python date.weekday()
def generate_breadlist(day):
    """
    Generates a new breadlist.
    """
    active_people = db.query(Person).filter_by(active=True).all()
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