from datetime import datetime

from .. import db


class Tokens(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_auth_provider_id = db.Column(db.Integer, db.ForeignKey('user_auth_providers.id'))
    token = db.Column(db.Text, unique=True, nullable=False)
    refresh_token = db.Column(db.Text, unique=True, nullable=False)
    revoked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
