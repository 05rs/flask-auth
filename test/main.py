from dotenv import load_dotenv

dotenv_path = '../local.env'
load_dotenv(dotenv_path)

import flask_auth_wrapper

app = flask_auth_wrapper.create_app('flask_auth_wrapper.config.Config')

if __name__ == '__main__':
    app.run(host='localhost', port=8080)
