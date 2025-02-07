from sqlalchemy.sql import expression

from .. import db


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    enabled = db.Column(db.Boolean, server_default=expression.true())
    auth_providers = db.relationship('UserAuthProviders', backref='user')