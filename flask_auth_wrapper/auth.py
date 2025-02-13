import logging
import os
from authlib.integrations.base_client import MismatchingStateError
from flask import Blueprint, request, jsonify, session, url_for, render_template, redirect

from . import oauth, db
from .decorators import token_required
from .exceptions import UserNotFoundException, InvalidProviderError, InvalidRefreshTokenError, ValidationError
from .models.tokens_model import Tokens
from .services.services import find_user_and_provider, update_user_auth_provider, add_token, validate_refresh_token, \
    revoke_tokens, get_user_auth_provider_by_token, get_user_provider_by_user_auth_provider, get_user_details
from .utils import create_access_token, generate_refresh_token

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.errorhandler(Exception)
def handle_auth_error(ex):
    logger.error(f"Exception in endpoint {request.endpoint}: {ex}", exc_info=True)

    def response(code: int, message: str, details: dict = None, error_type: str = None):
        response_data = {
            'code': code,
            'message': message
        }
        if details:
            response_data['details'] = details
        if error_type:
            response_data['error_type'] = error_type
        return jsonify(response_data), code

    if isinstance(ex, MismatchingStateError):
        return response(code=403, message=ex.description, error_type='CSRFError')


    if isinstance(ex, (InvalidProviderError, InvalidRefreshTokenError, ValidationError, UserNotFoundException)):
        return response(code=ex.code, message=ex.message, details=ex.details, error_type=ex.__class__.__name__)

    # Handle errors specific to the auth blueprint
    return response(code=500, message='something went wrong...')


@auth_bp.route('/')
def homepage():
    user = session.get('user')
    logger.info(f"Homepage accessed. User: {user}")
    return render_template('home.html', user=user)


@auth_bp.route('/login/<provider>')
def login(provider):
    logger.info(f"Login attempt for provider: {provider}")
    client = oauth.create_client(provider)
    if not client:
        logger.error(f"OAuth client for provider '{provider}' not found")
        raise InvalidProviderError(f"OAuth client for provider '{provider}' not found.")
    redirect_uri = url_for('auth.auth', provider=provider, _external=True, _scheme=os.environ.get('REDIRECT_URL_SCHEME', 'http'))
    logger.debug(f"Redirect URI generated: {redirect_uri}")
    return client.authorize_redirect(redirect_uri)


@auth_bp.route('/login', methods=['POST'])
def local_login():
    email = request.form.get('email')
    password = request.form.get('password')
    logger.info(f"Local login attempt. Email: {email}")

    if not email or not password:
        logger.warning("Missing email or password")
        return jsonify({'message': 'Missing email or password'}), 400

    existing_user, auth_provider = find_user_and_provider(email, 'local')
    user_auth_provider = update_user_auth_provider(user=existing_user, provider=auth_provider       )

    if not existing_user or password != user_auth_provider.password:
        logger.error("Invalid username or password")
        raise UserNotFoundException('Invalid username or password')

    access_token = create_access_token(existing_user, user_auth_provider)
    refresh_token = generate_refresh_token()
    logger.info(f"Generated tokens for user: {email}")

    revoked_tokens = revoke_tokens(user_auth_provider=user_auth_provider)

    token = add_token(
        user_auth_provider=user_auth_provider,
        access_token=access_token,
        refresh_token=refresh_token
    )

    db.session.add(user_auth_provider)
    db.session.add(token)
    db.session.commit()

    return jsonify({'access_token': access_token, 'refresh_token': refresh_token})


@auth_bp.route('<provider>')
def auth(provider):
    logger.info(f"OAuth callback for provider: {provider}")
    client = oauth.create_client(provider)
    token = client.authorize_access_token()
    user_info = token.get('userinfo') or client.userinfo()

    user_email = user_info.get('email')

    if not user_email:
        logger.error("Oauth: Did not received user email in metadata")
        return jsonify({'message': 'Something went wrong...'}), 400

    logger.info(f"User authenticated with email: {user_email}")

    # find user and provider
    existing_user, auth_provider = find_user_and_provider(user_email, provider)

    user_auth_provider = update_user_auth_provider(user=existing_user, provider=auth_provider, user_info=user_info)

    access_token = create_access_token(existing_user, user_auth_provider)
    refresh_token = generate_refresh_token()

    logger.info(f"Generated tokens for user: {user_email}")

    revoked_tokens = revoke_tokens(user_auth_provider=user_auth_provider)

    token = add_token(
        user_auth_provider=user_auth_provider,
        access_token=access_token,
        refresh_token=refresh_token
    )

    db.session.add(user_auth_provider)
    db.session.add(token)
    db.session.commit()
    frontend_redirect_url = os.getenv("FRONTEND_REDIRECT_URL", "http://localhost:4200/auth/sign-in")
    return redirect(f"{frontend_redirect_url}?access_token={access_token}&refresh_token={refresh_token}")



@auth_bp.route('/refresh', methods=['GET'])
def refresh():
    auth_header = request.headers.get('Authorization', None)
    if not auth_header:
        logger.warning("Missing Authorization header")
        return jsonify({'message': 'Authorization header missing'}), 400

    try:
        refresh_token = auth_header.split()[1]
    except IndexError:
        logger.error("Invalid Authorization header format")
        return jsonify({'message': 'Invalid Authorization header format. Expected: Bearer <token>'}), 400

    refresh_token = request.headers.get('Authorization').split()[1]
    if not refresh_token:
        return jsonify({'message': 'Missing refresh token'}), 400

    logger.info("Refreshing tokens")
    _token = validate_refresh_token(refresh_token)
    user_auth_provider = get_user_auth_provider_by_token(_token)
    user, provider = get_user_provider_by_user_auth_provider(user_auth_provider)
    if not user:
        logger.error("User not found or disabled")
        raise UserNotFoundException('User not found or disabled')

    new_access_token = create_access_token(user, user_auth_provider)
    new_refresh_token = generate_refresh_token()

    logger.info(f"Generated new tokens for user: {user.email}")

    revoke_tokens(token=_token)
    new_token = add_token(
        user_auth_provider=user_auth_provider,
        access_token=new_access_token,
        refresh_token=new_refresh_token
    )
    db.session.add(new_token)

    db.session.commit()

    return jsonify({'access_token': new_access_token, 'refresh_token': new_refresh_token})


@auth_bp.route('/whoami')
@token_required
def whoami(ua_id, user_email, **kwargs):
    logger.info(f"Received request for who_am_i")
    user_details = get_user_details(ua_id, user_email)
    _user_name = user_details.get('name')

    response = dict(
        message=f'Welcome {_user_name}!',
        details=user_details
    )
    return jsonify(response)


@auth_bp.route('/logout')
@token_required
def logout(**kwargs):
    logger.info(f"Received request for logout")
    auth_header = request.headers.get('Authorization')
    request_token = auth_header.split()[1]
    _token = Tokens.query.filter_by(token=request_token)
    revoke_tokens(token=_token)
    db.session.commit()
    _message = f"{kwargs.get('user_email', 'User')} successfully logged out."
    logger.info(_message)
    return jsonify(dict(message=_message))
