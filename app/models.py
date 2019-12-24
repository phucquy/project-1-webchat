from flask_login import UserMixin
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from . import db
from . import ma
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key =True)
    email = db.Column(db.String(200), nullable = False, unique=True)
    phone = db.Column(db.String(200), nullable = False, unique=True)
    username = db.Column(db.String(200), nullable = False, unique=True)
    password = db.Column(db.String(200), nullable = False)
    status = db.Column(db.Boolean, default=False, nullable=False)
    image = db.Column(db.String(200), default='image.jpg')

    def __repr__(self):
        return '<Task %r>' %self.id

#model Message
class Message(db.Model):
    id = db.Column(db.Integer, primary_key =True)
    user_1 = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    user_2 = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    content = db.Column(db.String(500), nullable = False)
    datetime = db.Column(db.DateTime, nullable = False)

    def __repr__(self):
        return '<Task %r>' %self.id

#mashmallow for model
class UserSchema(ma.ModelSchema):
    class Meta:
        model = User

class MesssageSchema(ma.ModelSchema):
    class Meta:
        model = Message
        include_fk = True
