from datetime import datetime

from .. import db


class Tokens(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_auth_provider_id = db.Column(db.Integer, db.ForeignKey('user_auth_providers.id'))
    token = db.Column(db.String(255), unique=True)
    refresh_token = db.Column(db.String(255), unique=True)
    revoked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    token_expires_at = db.Column(db.DateTime)
    refresh_token_expires_at = db.Column(db.DateTime)
