# el modo debug solo funciona con la ruta completa: py C:\Users\uidk4253\Documents\OpenAnalytics\OpenAnalytics\Flask\mainFlask.py

from flask import Flask
from Logger import flaskLogger as Log
import dotenv
import os

app = Flask(__name__)


@app.route('/')
def index():
    return "Hola Mundo caMds asasas!"

@app.route('/test')
def test():
    return "test"


if __name__ == '__main__':
    dotenv.load_dotenv(dotenv.find_dotenv())
    port = os.getenv("FLASK_PORT")
    debug = bool(os.getenv("FLASK_DEBUG"))

    Log.info(f"Flask server initilized port:{port} debug:{debug}")
    app.run(port=port, debug=debug)
