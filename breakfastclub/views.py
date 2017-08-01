from flask import Flask, render_template, request, redirect, url_for

from breakfastclub import app, db
from breakfastclub.models import Person


@app.route('/')
def index():
    return "Hello, world!"

@app.route('/people')
def show_people():
    people = db.session.query(Person.name, Person.email)
    return render_template('people.html', people=people)


@app.route('/people/add', methods=['POST', 'GET'])
def add_person():
    if request.method == 'POST':
        print("Hello")
        name = str(request.form['name'])
        email = str(request.form['email'])
        person = Person(name=name, email=email, active=True)
        db.session.add(person)
        db.session.commit()
        return redirect(url_for('show_people'))
    else:
        return render_template('add_person.html')


@app.route('/breadlist')
def show_breadlist():
    breadbringers = [{'date': '20-01-2017',
                      'name': 'Jesper',
                      'email': 'xyz@cs.au.dk'},
                     {'date': '27-01-2017',
                      'name': 'Gerth',
                      'email': 'abc@cs.au.dk'},]

    return render_template('breadlist.html', breadbringers=breadbringers)