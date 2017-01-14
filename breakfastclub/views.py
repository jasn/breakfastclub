from flask import Flask, render_template, request


from breakfastclub import app
from breakfastclub.models import Person, Session


@app.route('/')
def index():
    return "Hello, world!"

@app.route('/people')
def show_people():
    session = Session()
    peeps = session.query(Person.name, Person.email)
    return render_template('people.html', people=peeps)


@app.route('/people/add', methods=['POST', 'GET'])
def add_person():
    if request.method == 'POST':
        print("Hello")
        name = str(request.form['name'])
        email = str(request.form['email'])
        person = Person(name=name, email=email, active=True)
        session = Session()
        session.add(person)
        session.commit()
        return show_people() # render_template('add_person.html')#, person_added=True)
    else:
        return render_template('add_person.html')#, person_added=False)


@app.route('/breadlist')
def show_breadlist():
    breadbringers = [{'date': '20-01-2017',
                      'name': 'Jesper',
                      'email': 'xyz@cs.au.dk'},
                     {'date': '27-01-2017',
                      'name': 'Gerth',
                      'email': 'abc@cs.au.dk'},]

    return render_template('breadlist.html', breadbringers=breadbringers)
