import os, sys, json, datetime
from flask import Flask, request, jsonify, redirect, url_for, render_template, session
from models import *
from dotenv import load_dotenv
load_dotenv()

if True in [x not in os.environ for x in ["SERVER_PORT"]]:
    print("Please set all required environment variables in .env file.")
    sys.exit(1)

app = Flask(__name__)

def resetDB():
    acc1ID = None
    acc2ID = None

    ## Create sample accounts
    if "prakhar07062@gmail.com" not in [DI.data["accounts"][x]["email"] for x in DI.data["accounts"]]:
        DI.data["accounts"][Universal.generateUniqueID()] = {
            "fullName": "John Doe",
            "email": "prakhar07062@gmail.com",
            "password": "123456"
        }
    else:
        acc1ID = [x for x in DI.data["accounts"] if DI.data["accounts"][x]["email"] == "prakhar07062@gmail.com"][0]
    
    if "prakhar@prakhartrivedi.works" not in [DI.data["accounts"][x]["email"] for x in DI.data["accounts"]]:
        DI.data["accounts"][Universal.generateUniqueID()] = {
            "fullName": "Sarah Jones",
            "email": "prakhar@prakhartrivedi.works",
            "password": "123456"
        }
    else:
        acc2ID = [x for x in DI.data["accounts"] if DI.data["accounts"][x]["email"] == "prakhar@prakhartrivedi.works"][0]

    # Create 3 sample compliments
    DI.data["compliments"] = {
        Universal.generateUniqueID(): {
            "from": acc2ID,
            "to": acc1ID,
            "text": "You are awesome!",
            "imgName": "sample",
            "isAnonymous": True,
            "recipientAcknowledged": False,
            "datetime": datetime.datetime.now().strftime(Universal.systemWideStringDatetimeFormat)
        },
        Universal.generateUniqueID(): {
            "from": acc2ID,
            "to": acc1ID,
            "text": "Thank you so much for helping me!",
            "imgName": "sample",
            "isAnonymous": False,
            "recipientAcknowledged": True,
            "datetime": datetime.datetime.now().strftime(Universal.systemWideStringDatetimeFormat)
        },
        Universal.generateUniqueID(): {
            "from": acc1ID,
            "to": acc2ID,
            "text": "Stay awesome!",
            "imgName": "sample",
            "isAnonymous": False,
            "recipientAcknowledged": False,
            "datetime": datetime.datetime.now().strftime(Universal.systemWideStringDatetimeFormat)
        }
    }
    
    DI.save()

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

    ## Boilerplate setup
    if not ("BoilerplateDisabled" in os.environ and os.environ["BoilerplateDisabled"] == "True"):
        resetDB()
        print("Boilerplate setup complete (Set BoilerplateDisabled to True to disable).")

    # Blueprint registration
    from api import apiBP
    app.register_blueprint(apiBP)

    print()
    print("Boot pre-processing complete; all services online. Booting...")
    Logger.log("MAIN: Server booted.")

    app.run(host="0.0.0.0", port=os.environ["SERVER_PORT"])