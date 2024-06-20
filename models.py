import os, json, sys, random, datetime, copy, base64, uuid, requests, time, json
from passlib.hash import sha256_crypt as sha
from wrappers import *
from dotenv import load_dotenv
load_dotenv()

def fileContent(filePath, passAPIKey=False):
    with open(filePath, 'r') as f:
        f_content = f.read()
        if passAPIKey:
            f_content = f_content.replace("\{{ API_KEY }}", os.getenv("API_KEY"))
        return f_content

class DI:
    data = []
    syncStatus = True

    sampleData = {
        "accounts": {},
        "compliments": {}
    }

    @staticmethod
    def setup():
        if not os.path.exists(os.path.join(os.getcwd(), "database.txt")):
            with open("database.txt", "w") as f:
                json.dump(DI.sampleData, f)
        
        if FireRTDB.checkPermissions():
            try:
                if not FireConn.connected:
                    print("DI-FIRECONN: Firebase connection not established. Attempting to connect...")
                    response = FireConn.connect()
                    if response != True:
                        print("DI-FIRECONN: Failed to connect to Firebase. Aborting setup.")
                        return response
                    else:
                        print("DI-FIRECONN: Firebase connection established. Firebase RTDB is enabled.")
                else:
                    print("DI: Firebase RTDB is enabled.")
            except Exception as e:
                print("DI FIRECONN ERROR: " + str(e))
                return "Error"
            
        return DI.load()
    
    @staticmethod
    def load():
        try:
            ## Check and create database file if it does not exist
            if not os.path.exists(os.path.join(os.getcwd(), "database.txt")):
                with open("database.txt", "w") as f:
                    json.dump(DI.sampleData, f)

            def loadFromLocalDBFile():
                loadedData = []
                # Read data from local database file
                with open("database.txt", "r") as f:
                    loadedData = json.load(f)

                ## Carry out structure enforcement
                changesMade = False
                for topLevelKey in DI.sampleData:
                    if topLevelKey not in loadedData:
                        loadedData[topLevelKey] = DI.sampleData[topLevelKey]
                        changesMade = True

                if changesMade:
                    # Local database structure needs to be updated
                    with open("database.txt", "w") as f:
                        json.dump(loadedData, f)

                # Load data into DI
                DI.data = loadedData
                return

            if FireRTDB.checkPermissions():
                # Fetch data from RTDB
                fetchedData = FireRTDB.getRef()
                if isinstance(fetchedData, str) and fetchedData.startswith("ERROR"):
                    # Trigger last resort of local database (Auto-repair)
                    print("DI-FIRERTDB GETREF ERROR: " + fetchedData)
                    print("DI: System will try to resort to local database to load data to prevent a crash. Attempts to sync with RTDB will continue.")

                    loadFromLocalDBFile()
                    DI.syncStatus = False
                    return "Success"
                
                # Translate data for local use
                fetchedData = FireRTDB.translateForLocal(fetchedData)
                if isinstance(fetchedData, str) and fetchedData.startswith("ERROR"):
                    # Trigger last resort of local database (Auto-repair)
                    print("DI-FIRERTDB TRANSLATELOCAL ERROR: " + fetchedData)
                    print("DI: System will try to resort to local database to load data to prevent a crash. Attempts to sync with RTDB will continue.")

                    loadFromLocalDBFile()
                    DI.syncStatus = False
                    return "Success"
                
                # Carry out structure enforcement
                changesMade = False
                for topLevelKey in DI.sampleData:
                    if topLevelKey not in fetchedData:
                        fetchedData[topLevelKey] = DI.sampleData[topLevelKey]
                        changesMade = True

                if changesMade:
                    # RTDB structure needs to be updated
                    response = FireRTDB.setRef(FireRTDB.translateForCloud(fetchedData))
                    if response != True:
                        print("DI-FIRERTDB SETREF ERROR: " + response)
                        print("DI: Failed to update RTDB structure. System will continue to avoid a crash but attempts to sync with RTDB will continue.")
                        DI.syncStatus = False

                # Write data to local db file
                with open("database.txt", "w") as f:
                    json.dump(fetchedData, f)
                
                # Load data into DI
                DI.data = fetchedData
            else:
                loadFromLocalDBFile()
                DI.syncStatus = True
                return "Success"
        except Exception as e:
            print("DI ERROR: Failed to load data from database; error: {}".format(e))
            return "Error"
        return "Success"
    
    @staticmethod
    def save():
        try:
            with open("database.txt", "w") as f:
                json.dump(DI.data, f)
            DI.syncStatus = True

            # Update RTDB
            if FireRTDB.checkPermissions():
                response = FireRTDB.setRef(FireRTDB.translateForCloud(DI.data))
                if response != True:
                    print("DI FIRERTDB SETREF ERROR: " + response)
                    print("DI: System will resort to local database to prevent a crash. Attempts to sync with RTDB will continue.")
                    DI.syncStatus = False
                    # Continue runtime as system can function without cloud database
        except Exception as e:
            print("DI ERROR: Failed to save data to database; error: {}".format(e))
            DI.syncStatus = False
            return "Error"
        return "Success"
    
class Universal:
    '''This class contains universal methods and variables that can be used across the entire project. Project-wide standards and conventions (such as datetime format) are also defined here.'''

    systemWideStringDatetimeFormat = "%Y-%m-%d %H:%M:%S"
    copyright = "© 2024 KudosU. All Rights Reserved."

    @staticmethod
    def generateUniqueID(customLength=None, notIn=None):
        if customLength == None:
            randomID = uuid.uuid4().hex

            return randomID
        else:
            options = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
            randomID = ''
            while randomID == "" or ((notIn != None) and (randomID in notIn)):
                for i in range(customLength):
                    randomID += random.choice(options)
            return randomID

