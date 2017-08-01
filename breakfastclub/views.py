from flask import Flask, render_template, request, redirect, url_for
from flask_login import login_user, login_required

from breakfastclub import app, db
from breakfastclub.models import Person, BreadList

from breakfastclub.forms import AddPersonForm, ShowLoginForm

@app.route('/')
def index():
    return "Hello, world!"

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
        return redirect(url_for('show_successful_login'))
    return render_template('login.html', form=form)

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
