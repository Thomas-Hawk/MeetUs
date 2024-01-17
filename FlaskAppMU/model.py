from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Account(db.Model): # Modèle
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    eventname = db.Column(db.String(50), nullable=False)
    number_questions_person = db.Column(db.Integer, default=3)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    id_account = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)


class Guest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(50), nullable=False)
    lname = db.Column(db.String(50), nullable=False)
    job = db.Column(db.String(50))
    age = db.Column(db.Integer)
    sex = db.Column(db.Integer)
    hobby_1 = db.Column(db.String(255))
    hobby_2 = db.Column(db.String(255))
    hobby_3 = db.Column(db.String(255))
    questions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    id_event = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)


class Whoknowswho(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guest = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    know_him = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)