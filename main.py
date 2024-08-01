from dotenv import load_dotenv

dotenv_path = './local.env'
load_dotenv(dotenv_path)

from flask_auth_wrapper import create_app

app = create_app('flask_auth_wrapper.config.Config')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
