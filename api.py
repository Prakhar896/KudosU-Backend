import os, sys, json, datetime, copy
from flask import Blueprint, request, jsonify, redirect, url_for, render_template, session
from main import DI, Universal, resetDB

apiBP = Blueprint('api', __name__)

def checkCredentials(requestBody):
    if "email" not in requestBody:
        return "ERROR: Email not provided."
    if "password" not in requestBody:
        return "ERROR: Password not provided."

    for accountID in DI.data["accounts"]:
        if DI.data["accounts"][accountID]["email"] == requestBody["email"] and DI.data["accounts"][accountID]["password"] == requestBody["password"]:
            return accountID
        
    return "ERROR: Invalid credentials."

@apiBP.route("/api/health", methods=["GET"])
def health():
    return "SUCCESS: Healthy!", 200

@apiBP.route("/api/resetDB", methods=["GET"])
def resetDB():
    accessKey = request.args.get("accessKey")
    if accessKey != os.environ.get("AccessKey", None):
        return "ERROR: Access key is invalid.", 401
    try:
        resetDB()
    except Exception as e:
        return "ERROR: Failed to reset database. Error: {}".format(e), 500
    
    return "SUCCESS: Database reset.", 200

@apiBP.route("/api/login", methods=["POST"])
def login():
    if not request.is_json:
        return "ERROR: Request body is not JSON.", 400

    requestBody = copy.deepcopy(request.json)
    response = checkCredentials(requestBody)
    if response.startswith("ERROR"):
        return response, 401

    return "SUCCESS: Logged in.", 200

@apiBP.route("/api/getCompliments", methods=["POST"])
def getCompliments():
    if not request.is_json:
        return "ERROR: Request body is not JSON.", 400

    requestBody = copy.deepcopy(request.json)
    accID = checkCredentials(requestBody)
    if accID.startswith("ERROR"):
        return accID, 401
    
    userAddressedCompliments = {}
    dbChangesMade = False
    for complimentID in DI.data["compliments"]:
        if DI.data["compliments"][complimentID]["to"] == accID:
            ## Process compliment and simplify for client-use
            processedCompliment = copy.deepcopy(DI.data["compliments"][complimentID])
            if processedCompliment["isAnonymous"] == True:
                processedCompliment["from"] = "Anonymous"
            else:
                if processedCompliment["from"] in DI.data["accounts"]:
                    processedCompliment["from"] = DI.data["accounts"][processedCompliment["from"]]["fullName"]
                else:
                    processedCompliment["from"] = "Unknown"
            
            processedCompliment["to"] = DI.data["accounts"][accID]["fullName"]
            
            ## Add compliment to user-addressed compliments
            userAddressedCompliments[complimentID] = processedCompliment

            ## Mark unacknowledged compliments as acknowledged
            if DI.data["compliments"][accID]["recipientAcknowledged"] != True:
                DI.data["compliments"][accID]["recipientAcknowledged"] = True
                dbChangesMade = True
    
    if dbChangesMade:
        DI.save()
    
    return jsonify(userAddressedCompliments), 200

@apiBP.route('/api/getSentiment', methods=["POST"])
def getSentiment():
    if not request.is_json:
        return "ERROR: Request body is not JSON.", 400
    
    textToBeAnalysed = request.json["text"]
    