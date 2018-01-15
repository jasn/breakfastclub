import datetime

import click

from flask import url_for
from flask_mail import Message

from breakfastclub import app, db, mail
from breakfastclub.models import Person, BreadList


@app.cli.command('send-mail-list-running-out')
@click.option('-n', '--dry-run', is_flag=True)
def send_mail_list_running_out(dry_run):
    qs = db.session.query(BreadList)
    qs = qs.order_by(BreadList.date.desc())
    last_date = qs.first().date
    today = datetime.date.today()
    if (last_date - today).days > 7:
        print("More than one week remaining in the list.")
        return

    qs = db.session.query(Person)
    qs = qs.filter(Person.is_admin == True)  # noqa
    admins = qs.all()
    subject = "[Breakfastclub] The list is running out."
    body_template = """Dear administrator,
The breakfastclub bread list is running out and a new
one needs to be generated.

Please log in at
{link}
And generate a new list.

Best regards,
The Breakfastclub
"""
    from flask.ctx import AppContext
    # flask cannot do url_for when no requests have been made and SERVER_NAME
    # is unset
    app.config['SERVER_NAME'] = 'dummy'
    with AppContext(app):
        for admin in admins:
            login_link = (app.config['SITE_ADDRESS'] +
                          url_for('attempt_login', token=admin.token, _external=False))
            body = body_template.format(link=login_link)
            email_message = Message(sender=app.config['EMAIL_SENDER'],
                                    recipients=[admin.email],
                                    subject=subject,
                                    body=body)
            if not dry_run:
                mail.send(email_message)
            else:
                print(email_message)
    return


@app.cli.command('send-mail-reminder')
@click.option('-n', '--dry-run', is_flag=True)
# 1 is tuesday, following python date.weekday()
def send_mail_reminder(dry_run):
    text_message = """Hi {name}

It is your turn to bring breakfast on {date}.

Best regards,
The Breakfastclub
"""
    subject = "[Breakfastclub] Reminder"
    today = datetime.date.today()
    week = datetime.timedelta(7)
    qs = db.session.query(BreadList).filter(BreadList.date >= today)
    qs = qs.filter(BreadList.date < today+week)
    qs = qs.order_by(BreadList.date)
    up_next = qs.first()
    if up_next is None:
        print("No person to receive notification")
        return

    qs = db.session.query(Person)
    qs = qs.filter(Person.active == True)  # noqa
    count = qs.count()

    text_message = text_message.format(name=up_next.person.name,
                                       date=up_next.date,
                                       count=count)
    email_message = Message(sender=app.config['EMAIL_SENDER'],
                            recipients=[up_next.person.email],
                            subject=subject,
                            body=text_message)
    if dry_run:
        print(email_message)
    else:
        mail.send(email_message)
