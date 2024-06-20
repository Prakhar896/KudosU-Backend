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
        
class FireRTDB:
    @staticmethod
    def checkPermissions():
        '''Returns True if permission is granted, otherwise returns False.'''
        if 'FireRTDBEnabled' in os.environ and os.environ['FireRTDBEnabled'] == 'True':
            return True
        return False

    @staticmethod
    def clearRef(refPath="/"):
        '''Returns True upon successful update. Providing `refPath` is optional; will be the root reference if not provided.'''
        if not FireRTDB.checkPermissions():
            return "ERROR: FireRTDB service operation permission denied."
        try:
            ref = db.reference(refPath)
            ref.set({})
        except Exception as e:
            return "ERROR: Error occurred in clearing children at that ref; error: {}".format(e)
        return True

    @staticmethod
    def setRef(data, refPath="/"):
        '''Returns True upon successful update. Providing `refPath` is optional; will be the root reference if not provided.'''
        if not FireRTDB.checkPermissions():
            return "ERROR: FireRTDB service operation permission denied."
        try:
            ref = db.reference(refPath)
            ref.set(data)
        except Exception as e:
            return "ERROR: Error occurred in setting data at that ref; error: {}".format(e)
        return True

    @staticmethod
    def getRef(refPath="/"):
        '''Returns a dictionary of the data at the specified ref. Providing `refPath` is optional; will be the root reference if not provided.'''
        if not FireRTDB.checkPermissions():
            return "ERROR: FireRTDB service operation permission denied."
        data = None
        try:
            ref = db.reference(refPath)
            data = ref.get()
        except Exception as e:
            return "ERROR: Error occurred in getting data from that ref; error: {}".format(e)
        
        if data == None:
            return {}
        else:
            return data
        
    @staticmethod
    def recursiveReplacement(obj, purpose):
        dictValue = {} if purpose == 'cloud' else 0
        dictReplacementValue = 0 if purpose == 'cloud' else {}

        arrayValue = [] if purpose == 'cloud' else 1
        arrayReplacementValue = 1 if purpose == 'cloud' else []

        data = copy.deepcopy(obj)

        for key in data:
            if isinstance(data, list):
                # This if statement forbids the following sub-data-structure: [{}, 1, {}] (this is an example)
                continue

            if isinstance(data[key], dict):
                if data[key] == dictValue:
                    data[key] = dictReplacementValue
                else:
                    data[key] = FireRTDB.recursiveReplacement(data[key], purpose)
            elif isinstance(data[key], list):
                if data[key] == arrayValue:
                    data[key] = arrayReplacementValue
                else:
                    data[key] = FireRTDB.recursiveReplacement(data[key], purpose)
            elif isinstance(data[key], bool):
                continue
            elif isinstance(data[key], int) and purpose == 'local':
                if data[key] == 0:
                    data[key] = {}
                elif data[key] == 1:
                    data[key] = []

        return data
    
    @staticmethod
    def translateForLocal(fetchedData):
        '''Returns a translated data structure that can be stored locally.'''
        tempData = copy.deepcopy(fetchedData)

        try:
            # Null object replacement
            tempData = FireRTDB.recursiveReplacement(obj=tempData, purpose='local')

            # Other back-translation processes
            
        except Exception as e:
            return "ERROR: Error in translating fetched RTDB data for local system use; error: {}".format(e)
        
        return tempData
    
    @staticmethod
    def translateForCloud(loadedData):
        '''Returns a translated data structure that can be stored in the cloud.'''
        tempData = copy.deepcopy(loadedData)

        ## Translation processes

        # Null object replacement
        tempData = FireRTDB.recursiveReplacement(obj=tempData, purpose='cloud')

        return tempData