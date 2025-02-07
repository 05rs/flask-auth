from functools import wraps
from flask import request, jsonify
from .utils import decode_access_token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'message': 'Missing authorization token'}), 401

        token = auth_header.split()[1]  # Assuming 'Bearer' format
        payload = decode_access_token(token)
        if not payload:
            return jsonify({'message': 'Invalid token'}), 401

        kwargs['user'] = {'id': payload.get('id')}
        return f(*args, **kwargs)
    return decorated
