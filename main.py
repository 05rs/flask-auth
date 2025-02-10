from dotenv import load_dotenv

dotenv_path = './local.env'
load_dotenv(dotenv_path)
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from flask_auth_wrapper import create_app


app = create_app('flask_auth_wrapper.config.Config')

if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)

