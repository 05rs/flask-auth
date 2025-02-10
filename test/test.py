import os

from dotenv import load_dotenv

dotenv_path = '../local.env'
load_dotenv(dotenv_path)

import flask_auth_wrapper
template_path = os.path.join(os.path.dirname(__file__), 'templates')
app = flask_auth_wrapper.create_app('flask_auth_wrapper.config.Config', template_folder=template_path)

if __name__ == '__main__':
    app.run(host='localhost', port=8080)
