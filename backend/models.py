from datetime import datetime
from database import db

class Legislation(db.Model):
    __tablename__ = 'legislation'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    full_text = db.Column(db.Text)
    summary = db.Column(db.Text)
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    clauses = db.relationship('Clause', backref='legislation', lazy=True)
    feedback = db.relationship('Feedback', backref='legislation', lazy=True)

class Clause(db.Model):
    __tablename__ = 'clauses'
    id = db.Column(db.Integer, primary_key=True)
    legislation_id = db.Column(db.Integer, db.ForeignKey('legislation.id'), nullable=False)
    clause_number = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    summary = db.Column(db.Text)
    feedback = db.relationship('Feedback', backref='clause', lazy=True)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100))
    location = db.Column(db.String(100))
    age_group = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    feedback = db.relationship('Feedback', backref='user', lazy=True)

class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    legislation_id = db.Column(db.Integer, db.ForeignKey('legislation.id'), nullable=False)
    clause_id = db.Column(db.Integer, db.ForeignKey('clauses.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    sentiment_score = db.Column(db.Float)
    tags = db.Column(db.JSON)
    comment = db.Column(db.Text)
    demographic_data = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)