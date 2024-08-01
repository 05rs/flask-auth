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
        user_id = decode_access_token(token)
        if not user_id:
            return jsonify({'message': 'Invalid token'}), 401
        kwargs['user'] = {'user_id': user_id}
        return f(*args, **kwargs)
    return decorated
