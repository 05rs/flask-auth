import time
import uuid

import jwt
from flask import current_app


def create_access_token(user):
    payload = {'id': user.id, 'exp': time.time() + 3600}  # 1 hour expiry
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token


def generate_refresh_token():
    return uuid.uuid4().hex


def decode_access_token(token):
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return {'id': payload.get('id'), 'exp': payload.get('exp') }
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
