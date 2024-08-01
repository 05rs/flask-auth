import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

    OAUTH2_PROVIDERS = {
        'google': {

            'server_metadata_url': os.getenv('OAUTH2_GOOGLE_SERVER_METADATA_URL'),
            'client_kwargs': {'scope': os.getenv('OAUTH2_GOOGLE_CLIENT_SCOPE')}
        },
        'twitter': {
            'api_base_url': os.getenv('OAUTH2_TWITTER_API_BASE_URL'),
            'request_token_url': os.getenv('OAUTH2_TWITTER_REQUEST_TOKEN_URL'),
            'access_token_url': os.getenv('OAUTH2_TWITTER_ACCESS_TOKEN_URL'),
            'authorize_url': os.getenv('OAUTH2_TWITTER_AUTHORIZE_URL'),
            'userinfo_endpoint': os.getenv('OAUTH2_TWITTER_USERINFO_ENDPOINT'),
            'userinfo_compliance_fix': os.getenv('OAUTH2_TWITTER_USERINFO_COMPLIANCE_FIX')
        }
    }

    @staticmethod
    def init_app(app):
        pass  # Add any additional initialization here if needed

# import os
#
# GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '1007330140109-gfi7augnstg6si4of5j1is5n173s8ar9.apps.googleusercontent.com')
# GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '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')
#
# TWITTER_CLIENT_ID = os.getenv('TWITTER_CLIENT_ID')
# TWITTER_CLIENT_SECRET = os.getenv('TWITTER_CLIENT_SECRET')