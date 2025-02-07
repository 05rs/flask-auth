from .. import db


class UserAuthProviders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    auth_provider_id = db.Column(db.Integer, db.ForeignKey('auth_providers.id'))
    name = db.Column(db.String(255))
    photo = db.Column(db.String)
    password = db.Column(db.String(255))
    tokens = db.relationship('Tokens', backref='user_auth_providers')

