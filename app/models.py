from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    api_key = db.Column(db.String(128)) # Twelve Data API Key
    portfolios = db.relationship('Portfolio', backref='owner', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    type = db.Column(db.String(64)) # e.g., RRSP, TFSA
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    holdings = db.relationship('Holding', backref='portfolio', lazy='dynamic', cascade="all, delete-orphan")

class Holding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    units = db.Column(db.Float, nullable=False)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'), nullable=False)
