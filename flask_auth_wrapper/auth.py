from flask import Blueprint, request, jsonify, session, redirect, url_for, abort, render_template
from . import oauth, db
from .models import User
from .utils import create_access_token, generate_refresh_token
from .decorators import token_required

auth_bp = Blueprint('auth', __name__)





@auth_bp.route('/')
def homepage():
    user = session.get('user')
    return render_template('home.html', user=user)

@auth_bp.route('/login/<provider>')
def login(provider):
    client = oauth.create_client(provider)
    if not client:
        abort(404)
    redirect_uri = url_for('auth.auth', provider=provider, _external=True)
    return client.authorize_redirect(redirect_uri)

@auth_bp.route('/auth/<provider>')
def auth(provider):
    client = oauth.create_client(provider)
    if not client:
        abort(404)

    token = client.authorize_access_token()
    user_info = token.get('userinfo')
    if not user_info:
        user_info = client.userinfo()

    user_email = user_info.get('email')
    if not user_email:
        return redirect('/')

    access_token = create_access_token(user_email)
    existing_user = User.query.filter_by(email=user_email).first()
    if not existing_user:
        new_user = User(email=user_email, token=access_token, refresh_token=generate_refresh_token())
        db.session.add(new_user)
        db.session.commit()
    else:
        existing_user.token = access_token
        db.session.commit()

    return jsonify({'access_token': access_token})

@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    refresh_token = request.json.get('refresh_token')
    if not refresh_token:
        return jsonify({'message': 'Missing refresh token'}), 400

    user = User.query.filter_by(refresh_token=refresh_token).first()
    if not user:
        return jsonify({'message': 'Invalid refresh token'}), 401

    access_token = create_access_token(user.email)
    new_refresh_token = generate_refresh_token()

    user.token = access_token
    user.refresh_token = new_refresh_token
    db.session.commit()

    return jsonify({'access_token': access_token, 'refresh_token': new_refresh_token})

@auth_bp.route('/protected')
@token_required
def protected_route(user, **kwargs):
    return jsonify({'message': 'Welcome to the protected route!'})

@auth_bp.route('/logout')
@token_required
def logout(user, **kwargs):
    existing_user = User.query.filter_by(email=user.get('user_id')).first()
    if existing_user:
        existing_user.token = None
        db.session.commit()
    return redirect('/')
