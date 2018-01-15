import datetime

from flask import flash, render_template, request, redirect, url_for
from flask_login import login_user, login_required, current_user
from flask_mail import Message

from breakfastclub import app, db, login_manager, mail
from breakfastclub.models import Person, BreadList

from breakfastclub.forms import (
    AddPersonForm, ShowLoginForm, GenerateBreadListForm,
    get_token_management_form, ConfirmEmailNotifyForm
)


@app.route('/')
def index():
    breadlist = db.session.query(BreadList).order_by(BreadList.date.desc())
    today = datetime.date.today()
    try:
        next_bringer = min((b for b in breadlist if b.date >= today),
                           key=lambda b: b.date)
        next_bringer.is_next = True
    except ValueError:
        pass

    return render_template('index.html', breadbringers=breadlist)


@app.route('/generate_breadlist', methods=['GET', 'POST'])
def show_generate_breadlist():
    old_length_cap = 5  # to only show the true next_bringer.
    qs = db.session.query(BreadList)
    qs = qs.order_by(BreadList.date.desc()).limit(old_length_cap + 1)
    breadlist = qs.all()
    today = datetime.date.today()
    try:
        next_bringer = min((b for b in breadlist if b.date >= today),
                           key=lambda b: b.date)
        next_bringer.is_next = True
    except ValueError:
        pass
    breadlist = breadlist[:5]
    shuffle = bool(request.args.get('s'))
    form = GenerateBreadListForm(request.form, shuffle=shuffle)
    if request.method == 'POST' and form.validate():
        form.save()
        flash('Generated breadlist saved.')
        return redirect(url_for('index'))
    return render_template('generate_breadlist.html',
                           breadbringers=breadlist, form=form)


@app.route('/people')
@login_required
def show_people():
    people = db.session.query(Person).all()
    return render_template('people.html', people=people)


@app.route('/login/success')
@login_required
def show_successful_login():
    return render_template('login_successful.html')


@app.route('/login/<token>', methods=['GET'])
def attempt_login(token):
    qs = db.session.query(Person).filter(Person.token == token)
    person = qs.scalar()
    if person is None:
        return redirect(url_for('show_login'))
    login_user(person)
    flash('Login successful.')
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def show_login():
    form = ShowLoginForm(request.form)
    if request.method == 'POST' and form.validate():
        login_user(form.person)
        flash('Login successful.')
        return redirect(url_for('index'))
    return render_template('login.html', form=form)


login_manager.login_view = 'show_login'


@app.route('/signup', methods=['POST', 'GET'])
@login_required
def add_person():
    form = AddPersonForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        person = Person(name=name, email=email, active=True)
        db.session.add(person)
        db.session.commit()
        return redirect(url_for('show_people'))
    else:
        return render_template('add_person.html', form=form)


@app.route('/breadlist')
def show_breadlist():
    entries = db.session.query(BreadList).order_by(BreadList.date)
    return render_template('breadlist.html', breadbringers=entries)


@app.route('/deactivate')
@login_required
def deactivate_current_user():
    current_user.active = False
    db.session.add(current_user)
    db.session.commit()
    flash('You are now inactive.')
    return redirect(url_for('index'))


@app.route('/activate')
@login_required
def activate_current_user():
    current_user.active = True
    db.session.add(current_user)
    db.session.commit()
    flash('You are now active.')
    return redirect(url_for('index'))


@app.route('/token_management', methods=['POST', 'GET'])
@login_required
def token_management():
    people = db.session.query(Person).all()
    people = sorted(people, key=lambda p: p.name.lower())
    form = get_token_management_form(people)(request.form)
    if request.method == "POST" and form.validate():
        flash("Updated info.")
        return redirect(url_for('token_management'))
    return render_template('token_management.html', form=form)


@app.route('/breadlist_management')
@login_required
def breadlist_management():
    if not current_user.is_admin:
        flash('Only admins have access to the breadlist management.')
        return redirect(url_for('index'))
    return render_template('breadlist_management.html')


def send_notification_new_breadlist_coming(person):
    subject = "[Breakfastclub] Reminder: New bread list soon."
    message_template = """Hello {name}
This is a reminder that a new bread list will be generated soon.

If you no longer wish to partake in the breakfastclub you can sign in and deactivate yourself at the link below.
{link}

Best regards,
The Breakfastclub
"""
    body = message_template.format(name=person.name,
                                   link=url_for('attempt_login',
                                                token=person.token,
                                                _external=True))

    email_message = Message(subject=subject, body=body,
                            recipients=[person.email],
                            sender=app.config['EMAIL_SENDER'])
    mail.send(email_message)
    return


@app.route('/breadlist_management/confirm_notify', methods=['GET', 'POST'])
@login_required
def confirm_send_notify_new_breadlist():
    if not current_user.is_admin:
        flash('Only admins have access to the breadlist management.')
        return redirect(url_for('index'))
    form = ConfirmEmailNotifyForm(request.form)
    if request.method == "POST" and form.validate():
        people = db.session.query(Person).filter(Person.active == True).all()  # noqa
        count = 0
        for person in people:
            try:
                send_notification_new_breadlist_coming(person, mail_conn)
                count += 1
            except Exception:
                if count == 0:
                    flash("Something went wrong. No email sent.")
                    return redirect(url_for('index'))
                else:
                    msg = "Could not send an email to %s." % person.email
                    flash(msg)
        flash("Email notifications sent to {count}.".format(count=count))
        return redirect(url_for('index'))
    elif request.method == "POST":
        return redirect(url_for('breadlist_management'))
    return render_template('breadlist_confirm_send_notify.html', form=form)
