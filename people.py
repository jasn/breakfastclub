from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('mysql+mysqldb://jasn:monster@localhost/breakfastclub')
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Person(Base):
    __tablename__ = 'people'

    personId = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(200))

    def __repr__(self):
        return '<Person(name=%s, email=%s)>' % (name, email)
