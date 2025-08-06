#!/usr/bin/env python3
"""
Test script to verify Flask Admin functionality
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = 'test'

db = SQLAlchemy(app)

class TestModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

admin = Admin(app, name='Test Admin', template_mode='bootstrap3')
admin.add_view(ModelView(TestModel, db.session))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 