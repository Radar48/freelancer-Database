from __future__ import annotations  # helps with forward references
from flask_login import UserMixin
from typing import TYPE_CHECKING
from flask_login import UserMixin
from app import db


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    currency = db.Column(db.String(5), default="USD")
    income_entries = db.relationship("IncomeEntry", back_populates="user")

    def get_id(self):
        return str(self.user_id)

class Platform(db.Model):
    __tablename__ = 'platforms'
    platform_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)

    income_entries = db.relationship("IncomeEntry", back_populates="platform")

class Category(db.Model):
    __tablename__ = 'categories'
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)

    income_entries = db.relationship("IncomeEntry", back_populates="category")

class IncomeEntry(db.Model):
    __tablename__ = 'income_entries'
    entry_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    platform_id = db.Column(db.Integer, db.ForeignKey('platforms.platform_id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'))
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String)

    user = db.relationship("User", back_populates="income_entries")
    platform = db.relationship("Platform", back_populates="income_entries")
    category = db.relationship("Category", back_populates="income_entries")