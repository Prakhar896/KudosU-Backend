import os, sys, json, datetime
from flask import Flask, request, jsonify, redirect, url_for, render_template, session
from models import *
from dotenv import load_dotenv
load_dotenv()

if True in [x not in os.environ for x in ["SERVER_PORT"]]:
    print("Please set all required environment variables in .env file.")
    sys.exit(1)

app = Flask(__name__)

## Create 404 error handler
@app.errorhandler(404)
def page_not_found(e):
    return "ERROR: 404 Endpoint Not Found", 404

@app.route('/')
def index():
    return "Welcome to KudosU Backend Server."

if __name__ == '__main__':
    # Boot pre-processing

    ## Set up FireConn
    if FireConn.checkPermissions():
        response = FireConn.connect()
        if response != True:
            print("MAIN BOOT: Error in setting up FireConn; error: " + response)
            sys.exit(1)
        else:
            print("FIRECONN: Firebase connection established.")

    ## Set up DatabaseInterface
    response = DI.setup()
    if response != "Success":
        print("MAIN BOOT: Error in setting up DI; error: " + response)
        sys.exit(1)
    else:
        print("DI: Setup complete.")

    # Blueprint registration
    from api import apiBP
    app.register_blueprint(apiBP)

    app.run(host="0.0.0.0", port=os.environ["SERVER_PORT"])