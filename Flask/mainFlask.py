#! /home/hirvin/Documents/Dev/devEnv/bin/python3

# el modo debug solo funciona con la ruta completa: py C:\Users\uidk4253\Documents\OpenAnalytics\OpenAnalytics\Flask\mainFlask.py

from flask import Flask,jsonify
from Logger import flaskLogger as Log
import dotenv
import os
from flask_cors import CORS
import json
from GoogleApi import Contacts
from GoogleApi import Calendar

json_contacts = None
import io
contactsIO = io.StringIO()

# inti funtions
def init_services():
    """ firts function to init the server """
    Log.info("Init Services ...")
    contactsIO.write(Contacts.update_contact_list())
    if json_contacts is None:
        Log.error("Services hasen't been initialized.")
        return False
    Log.info("The services has been initialized succeful.")
    # print(json_contacts)
    return True

def testApi():
    Log.info("Iniciando test")

    Calendar.calendar_send_event(day=14)

# Flask server
app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return "Hola Mundo caMds asasas!"

@app.route('/test')
def test():
    data = {'some': 'data', 'casa':'arles'}
    # it is better the use of jsonify
    return jsonify(**data)

@app.route('/contacts')
def contacts():
    Log.info("Get /contacts")
    # if json_contacts is None:
    #    return "Invalid Contacts"
    return contactsIO.getvalue()
    # test = [{"data":1},{"data":2}]
    # return jsonify(test)

@app.route('/create')
def create_event():
    Log.info("Get /create")
    # Calendar.calendar_send_event(day=14)
    testApi()
    return jsonify("Sucess")

if __name__ == '__main__':
    # init services
    init_services()

    # start server
    dotenv.load_dotenv(dotenv.find_dotenv())
    port = os.getenv("FLASK_PORT")
    debug = bool(os.getenv("FLASK_DEBUG"))

    Log.info(f"Flask server initilized port:{port} debug:{debug}")
    print(contactsIO.getvalue())
    app.run(port=port, debug=debug)
