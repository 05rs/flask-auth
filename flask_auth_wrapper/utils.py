import os
import time
import uuid
import datetime

import jwt
from flask import current_app


def create_access_token(user, user_auth_provider):
    expiry_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=int(os.environ.get("TOKEN_EXPIRY", 600)))
    payload = {'ua_id': user_auth_provider.id,
               'user_email': user.email,
               'user_name': user_auth_provider.name,
               'exp': expiry_time,
               'iat': datetime.datetime.utcnow(),
               'jti': os.urandom(16).hex()
               }
    token = jwt.encode(payload, os.environ.get('SECRET_KEY'), algorithm='HS256')
    return token


def generate_refresh_token():
    return uuid.uuid4().hex


def decode_access_token(token):
    try:
        payload = jwt.decode(token, os.environ.get('SECRET_KEY'), algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
