from ..exceptions import InvalidRefreshTokenError, UserNotFoundException, \
    AuthProviderNotFoundException
from ..models.users_model import Users
from ..models.tokens_model import Tokens
from ..models.auth_providers_model import AuthProviders
from ..models.user_auth_providers_model import UserAuthProviders


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


def update_user_auth_provider(user, provider, user_info):
    user_auth_provider = UserAuthProviders.query.filter_by(user_id=user.id,
                                                           auth_provider_id=provider.id).first()
    if user_auth_provider:
        user_auth_provider.name = user_info.get('name')
        user_auth_provider.photo = user_info.get('picture')
    else:
        user_auth_provider = UserAuthProviders(
            user_id=user.id,
            auth_provider_id=provider.id,
            name=user_info.get('name'),
            photo=user_info.get('picture')
        )
    return user_auth_provider


def add_token(user, provider, access_token, refresh_token):
    return Tokens(
        user_id=user.id,
        auth_provider_id=provider.id,
        token=access_token,
        refresh_token=refresh_token,
        revoked=False
    )
