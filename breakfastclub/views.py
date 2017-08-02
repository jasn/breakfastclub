import datetime

from flask import flash, Flask, render_template, request, redirect, url_for
from flask_login import login_user, login_required

from breakfastclub import app, db, login_manager
from breakfastclub.models import Person, BreadList

from breakfastclub.forms import AddPersonForm, ShowLoginForm, GenerateBreadListForm

@app.route('/')
def index():
    breadlist = db.session.query(BreadList).order_by(BreadList.date.desc())
    today = datetime.date.today()
    next_bringer = min((b for b in breadlist if b.date >= today),
                       key=lambda b: b.date)
    next_bringer.is_next = True
    return render_template('index.html', breadbringers=breadlist)


@app.route('/generate_breadlist', methods=['GET', 'POST'])
def show_generate_breadlist():
    breadlist = list(db.session.query(BreadList).order_by(BreadList.date.desc()))
    today = datetime.date.today()
    next_bringer = min((b for b in breadlist if b.date >= today),
                       key=lambda b: b.date)
    next_bringer.is_next = True
    form = GenerateBreadListForm(request.form)
    if request.method == 'POST' and form.validate():
        form.save()
        flash('Generated breadlist saved.')
        return redirect(url_for('index'))
    return render_template('generate_breadlist.html', breadbringers=breadlist, form=form)


@app.route('/people')
def show_people():
    people = db.session.query(Person.name, Person.email)
    return render_template('people.html', people=people)


@app.route('/login/success')
@login_required
def show_successful_login():
    return render_template('login_successful.html')


@app.route('/login', methods=['GET', 'POST'])
def show_login():
    form = ShowLoginForm(request.form)
    if request.method == 'POST' and form.validate():
        login_user(form.person)
        flash('Login successful.')
        return redirect(url_for('index'))
    return render_template('login.html', form=form)
login_manager.login_view = 'show_login'


@app.route('/people/add', methods=['POST', 'GET'])
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
