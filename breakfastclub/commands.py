import datetime

import click

from flask_mail import Message

from breakfastclub import app, db, mail
from breakfastclub.models import Person, BreadList


@app.cli.command('send-mail-reminder')
@click.option('-n', '--dry-run', is_flag=True)
# 1 is tuesday, following python date.weekday()
def send_mail_reminder(dry_run):
    text_message = """Hello {name}.
You are bringing breakfast on {date}.
There are currently {count} people participating in the breakfastclub.
Best regards,
The Breakfastclub
"""
    subject = "[Breakfastclub] Reminder"
    today = datetime.date.today()
    qs = db.session.query(BreadList).filter(BreadList.date >= today)
    qs = qs.order_by(BreadList.date)
    up_next = qs.first()

    qs = db.session.query(Person)
    qs = qs.filter(Person.active == True)
    count = qs.count()

    text_message = text_message.format(name=up_next.person.name,
                                       date=up_next.date,
                                       count=count)
    email_message = Message(sender=app.config['EMAIL_REMINDER_SENDER'],
                            recipients=[up_next.person.email],
                            subject=subject,
                            body=text_message)
    if dry_run:
        print(email_message)
    else:
        mail.send(email_message)
