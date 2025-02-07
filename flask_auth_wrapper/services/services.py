from datetime import datetime, timezone

from ..exceptions import InvalidRefreshTokenError, UserNotFoundException, \
    AuthProviderNotFoundException
from ..models.auth_providers_model import AuthProviders
from ..models.tokens_model import Tokens
from ..models.user_auth_providers_model import UserAuthProviders
from ..models.users_model import Users


def validate_refresh_token(refresh_token):
    _token = Tokens.query.filter_by(refresh_token=refresh_token, revoked=False).first()
    if not _token:
        raise InvalidRefreshTokenError(message='Invalid Refresh Token!')
    return _token


def find_user_and_provider(user_email, provider):
    existing_user = Users.query.filter_by(email=user_email, enabled=True).first()
    if not existing_user:
        raise UserNotFoundException(message=f"User '{user_email}' not found or disabled!")

    auth_provider = AuthProviders.query.filter_by(name=provider).first()
    if not auth_provider:
        raise AuthProviderNotFoundException(message=f"Auth provider '{provider}' not supported")

    return existing_user, auth_provider


def get_user_by_token(token: Tokens):
    return Users.query.filter(Users.auth_providers.any(id=token.user_auth_provider_id), Users.enabled == True).first()

def get_profile_avatar(name):
    if name is None:
        return ""
    return f'https://ui-avatars.com/api/?background=random&color=%23ffffff&size=95&length=2&name={name}&font-size=0.55'

def update_user_auth_provider(user, provider, user_info={}):
    user_auth_provider = UserAuthProviders.query.filter_by(user_id=user.id,auth_provider_id=provider.id).first()

    if not user_auth_provider:
        user_auth_provider = UserAuthProviders(
            user_id=user.id,
            auth_provider_id=provider.id,
            name=user_info.get('name'),
            photo=user_info.get('picture', get_profile_avatar(user_info.get('name', None)))
        )
    else:
        if user_info.get('name'):
            user_auth_provider.name = user_info.get('name')

        # Update the photo if a picture is provided or if there's no existing photo
        if user_info.get('picture') or (user_auth_provider.name and not user_auth_provider.photo):
            user_auth_provider.photo = user_info.get('picture', None) or get_profile_avatar(user_auth_provider.name)

    return user_auth_provider


def revoke_tokens(token: Tokens = None, user_auth_provider: UserAuthProviders = None):
    if token:
        token.revoked = True
        return token
    if user_auth_provider:
        tokens = Tokens.query.filter_by(user_auth_provider_id=user_auth_provider.id, revoked=False)
        tokens.update({'revoked': True}, synchronize_session=False)
        return tokens


def add_token(user_auth_provider, access_token, refresh_token):
    return Tokens(
        user_auth_providers=user_auth_provider,
        token=access_token,
        refresh_token=refresh_token,
        revoked=False,
        created_at=datetime.now(tz=timezone.utc),
    )
