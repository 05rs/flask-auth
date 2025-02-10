from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth

db = SQLAlchemy()
oauth = OAuth()


def register_oauth_clients(app):
    for provider, config in app.config['OAUTH2_PROVIDERS'].items():
        oauth.register(
            name=provider,
            client_id=config.get('client_id'),
            client_secret=config.get('client_secret'),
            server_metadata_url=config.get('server_metadata_url'),
            api_base_url=config.get('api_base_url'),
            request_token_url=config.get('request_token_url'),
            access_token_url=config.get('access_token_url'),
            authorize_url=config.get('authorize_url'),
            userinfo_endpoint=config.get('userinfo_endpoint'),
            userinfo_compliance_fix=config.get('userinfo_compliance_fix'),
            client_kwargs=config.get('client_kwargs', {}),
            jwks_uri=config.get('jwks_uri')
        )


def create_app(config_object, **kwargs):
    app = Flask(__name__, **kwargs)
    app.config.from_object(config_object)

    db.init_app(app)
    oauth.init_app(app)

    register_oauth_clients(app)

    with app.app_context():
        from .auth import auth_bp
        app.register_blueprint(auth_bp)

        db.create_all()

    return app
