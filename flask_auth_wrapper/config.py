import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    OAUTH2_PROVIDERS = {
        'google': {
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
            'server_metadata_url': os.getenv('GOOGLE_METADATA_URL'),
            'client_kwargs': {'scope': 'openid email profile'}
        },
        'twitter': {
            'api_base_url': os.getenv('OAUTH2_TWITTER_API_BASE_URL'),
            'request_token_url': os.getenv('OAUTH2_TWITTER_REQUEST_TOKEN_URL'),
            'access_token_url': os.getenv('OAUTH2_TWITTER_ACCESS_TOKEN_URL'),
            'authorize_url': os.getenv('OAUTH2_TWITTER_AUTHORIZE_URL'),
            'userinfo_endpoint': os.getenv('OAUTH2_TWITTER_USERINFO_ENDPOINT'),
            'userinfo_compliance_fix': os.getenv('OAUTH2_TWITTER_USERINFO_COMPLIANCE_FIX')
        },
        'azure': {
            'client_id': os.getenv('AZURE_CLIENT_ID'),
            'client_secret': os.getenv('AZURE_CLIENT_SECRET'),
            'authorize_url': os.getenv('AZURE_AUTH_URL'),
            'access_token_url': os.getenv('AZURE_TOKEN_URL'),
            'client_kwargs': {'scope': 'openid email profile'},
            'jwks_uri': os.getenv('AZURE_JWKS_URL'),

        }
    }

    @staticmethod
    def init_app(app):
        pass  # Add any additional initialization here if needed
