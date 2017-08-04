from flask_login import UserMixin  # , AnonymousUserMixin

from breakfastclub import db


class Person(db.Model, UserMixin):
    __tablename__ = 'person'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(191),
                      nullable=False)  # varchar max length utf8mb4
    active = db.Column(db.Boolean, default=True, nullable=False)
    token = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    breadlist_set = db.relationship('BreadList', backref='person',
                                    lazy='dynamic')

    def __repr__(self):
        return '<Person(name=%s, email=%s)>' % (self.name, self.email)

    def __str__(self):
        return self.name

# For some strange reason the below code doesn't always
# replace the anonymous_user default with AnonymousPerson
# Maybe related to https://github.com/maxcountryman/flask-login/issues/261
#
# class AnonymousPerson(AnonymousUserMixin):
#     is_admin = False

# login_manager.anonymous_user = AnonymousPerson


class BreadList(db.Model):
    __tablename__ = 'breadlist'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    person_id = db.Column(db.Integer,
                          db.ForeignKey(Person.id,
                                        name='fk_breadlist_person_id'),
                          nullable=False)
