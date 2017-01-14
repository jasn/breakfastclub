import datetime
from random import shuffle

from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import ForeignKey
from sqlalchemy import func

import click

from breakfastclub import app

engine = create_engine('mysql+mysqlconnector://breakfast:monster@localhost/breakfastclub')
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Person(Base):
    __tablename__ = 'people'

    person_id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(200))
    active = Column(Boolean)
    def __repr__(self):
        return '<Person(name=%s, email=%s)>' % (self.name, self.email)


class breadlists(Base):
    __tablename__ = 'breadlists'

    id = Column(Integer, primary_key=True)


class bread_bringer(Base):
    __tablename__ = 'breadbringer'

    entry_id = Column(Integer, primary_key=True)
    breadlist_id = Column(Integer, ForeignKey('breadlists.id'))
    person_id = Column(Integer, ForeignKey('people.person_id'))
    date = Column(Date)

    def __repr__(self):
        return '<BreadlistEntry(person_id=%s, date=%s)>' % (self.person_id,
                                                            self.date)


@app.cli.command('initdb')
def initdb_command():
    """Initialize the database."""
    Base.metadata.create_all(engine)
    print("Database initialized")


@app.cli.command('generate-breadlist')
@click.option('--day', default=1)
# 1 is tuesday, following python date.weekday()
def generate_breadlist(day):
    """
    Generates a new breadlist.
    """
    session = Session()
    active_people = session.query(Person).filter_by(active=True).all()
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
