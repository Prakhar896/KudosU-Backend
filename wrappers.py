import os, sys, json, datetime, copy, uuid, re
from firebase_admin import db, storage, credentials, initialize_app
from firebase_admin import auth as adminAuth
from dotenv import load_dotenv
load_dotenv()

class FireConn:
    connected = False

    @staticmethod
    def checkPermissions():
        return ("FireConnEnabled" in os.environ and os.environ["FireConnEnabled"] == "True")

    @staticmethod
    def connect():
        '''Returns True upon successful connection.'''
        if not FireConn.checkPermissions():
            return "ERROR: Firebase connection permissions are not granted."
        if not os.path.exists("serviceAccountKey.json"):
            return "ERROR: Failed to connect to Firebase. The file serviceAccountKey.json was not found. Please re-read instructions for the Firebase addon."
        else:
            if 'RTDB_URL' not in os.environ:
                return "ERROR: Failed to connect to Firebase. RTDB_URL environment variable not set in .env file. Please re-read instructions for the Firebase addon."
            try:
                ## Firebase
                cred_obj = credentials.Certificate(os.path.join(os.getcwd(), "serviceAccountKey.json"))
                default_app = initialize_app(cred_obj, {
                    'databaseURL': os.environ["RTDB_URL"]
                })
                FireConn.connected = True
            except Exception as e:
                return "ERROR: Error occurred in connecting to RTDB; error: {}".format(e)
            return True