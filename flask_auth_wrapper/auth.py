import logging

from authlib.integrations.base_client import MismatchingStateError
from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template



from . import oauth, db, csrf
from .decorators import token_required
from .exceptions import UserNotFoundException, InvalidProviderError, InvalidRefreshTokenError, ValidationError
from .models.tokens_model import Tokens
from .services.services import find_user_and_provider, update_user_auth_provider, add_token, validate_refresh_token, \
    revoke_tokens, get_user_by_token
from .utils import create_access_token, generate_refresh_token

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)


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
    return render_template('home.html', user=user)


@auth_bp.route('/login/<provider>')
def login(provider):
    client = oauth.create_client(provider)
    if not client:
        raise InvalidProviderError(f"OAuth client for provider '{provider}' not found.")
    redirect_uri = url_for('auth.auth', provider=provider, _external=True)
    return client.authorize_redirect(redirect_uri)


@auth_bp.route('/login', methods=['POST'])
@csrf.exempt
def local_login():
    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        return jsonify({'message': 'Missing email or password'}), 400

    existing_user, auth_provider = find_user_and_provider(email, 'local')
    user_auth_provider = update_user_auth_provider(user=existing_user, provider=auth_provider       )

    if not existing_user or password != user_auth_provider.password:
        raise UserNotFoundException('Invalid username or password')

    access_token = create_access_token(existing_user)
    refresh_token = generate_refresh_token()

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


@auth_bp.route('/auth/<provider>')
def auth(provider):
    client = oauth.create_client(provider)
    token = client.authorize_access_token()
    user_info = token.get('userinfo') or client.userinfo()

    user_email = user_info.get('email')

    if not user_email:
        return redirect('/')

    # find user and provider
    existing_user, auth_provider = find_user_and_provider(user_email, provider)

    access_token = create_access_token(existing_user)
    refresh_token = generate_refresh_token()

    user_auth_provider = update_user_auth_provider(user=existing_user, provider=auth_provider, user_info=user_info)

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


@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    refresh_token = request.json.get('refresh_token')
    if not refresh_token:
        return jsonify({'message': 'Missing refresh token'}), 400

    _token = validate_refresh_token(refresh_token)
    user = get_user_by_token(_token)
    if not user:
        raise UserNotFoundException('User not found or disabled')

    new_access_token = create_access_token(user)
    new_refresh_token = generate_refresh_token()

    revoke_tokens(token=_token)
    new_token = add_token(
        user_auth_provider=_token.user_auth_provider,
        access_token=new_access_token,
        refresh_token=new_refresh_token
    )
    db.session.add(new_token)

    db.session.commit()

    return jsonify({'access_token': new_access_token, 'refresh_token': new_refresh_token})


@auth_bp.route('/protected')
@token_required
def protected_route(user, **kwargs):
    return jsonify({'message': f'Welcome {user} to the protected route!'})


@auth_bp.route('/logout')
@token_required
def logout(user, **kwargs):
    auth_header = request.headers.get('Authorization')
    request_token = auth_header.split()[1]
    _token = Tokens.query.filter_by(token=request_token)
    revoke_tokens(token=_token)
    db.session.commit()
    return redirect('/')
