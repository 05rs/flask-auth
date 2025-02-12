import logging
from functools import wraps
from flask import request, jsonify

from .exceptions import TokenExpiredException
from .utils import decode_access_token
logger = logging.getLogger(__name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        logger.info("Accessing protected route with token_required decorator")
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            logger.warning("Authorization header is missing")
            return jsonify({'message': 'Missing authorization token'}), 401

        try:
            token_type, token = auth_header.split()
            if token_type.lower() != 'bearer':
                logger.warning(f"Unexpected token type '{token_type}' in Authorization header")
                return jsonify({'message': 'Invalid token type. Expected Bearer'}), 401
        except ValueError:
            logger.error("Malformed Authorization header format")
            return jsonify({'message': 'Invalid Authorization header format. Expected: Bearer <token>'}), 401
        logger.debug(f"Authorization token received: {token}")
        try:
            payload = decode_access_token(token)
            if not payload:
                raise TokenExpiredException()
        except TokenExpiredException as e:
            logger.error(f"Token expired: {str(e)}")
            return jsonify(dict(message=e.message, code=e.code)), e.code
        payload.pop('exp', None)
        logger.debug(f"Token payload after decoding: {payload}")
        return f(*args, **payload)
    return decorated
