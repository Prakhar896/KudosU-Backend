import os, sys, json, datetime, copy
from flask import Blueprint, request, jsonify, redirect, url_for, render_template, session
from main import DI, Universal, resetDB, Emailer, Logger
from sentimentmodel import sentimentfunc

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

@apiBP.route("/api/reloadDI", methods=["GET"])
def reloadDI():
    accessKey = request.args.get("accessKey")
    if accessKey != os.environ.get("AccessKey", None):
        return "ERROR: Access key is invalid.", 401
    
    try:
        DI.load()
    except Exception as e:
        return "ERROR: Failed to reload DI. Error: {}".format(e), 500
    
    return "SUCCESS: DI reloaded.", 200

@apiBP.route("/api/logs", methods=["GET"])
def logs():
    accessKey = request.args.get("accessKey")
    if accessKey != os.environ.get("AccessKey", None):
        return "ERROR: Access key is invalid.", 401
    
    logs = Logger.readAll()
    if not isinstance(logs, list):
        return logs, 500
    
    return "<br>".join(logs), 200

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

            processedCompliment["imgURL"] = request.host_url + "static/" + processedCompliment["imgName"]
            
            ## Add compliment to user-addressed compliments
            userAddressedCompliments[complimentID] = processedCompliment

            ## Mark unacknowledged compliments as acknowledged
            if DI.data["compliments"][complimentID]["recipientAcknowledged"] != True:
                DI.data["compliments"][complimentID]["recipientAcknowledged"] = True
                dbChangesMade = True
    
    if dbChangesMade:
        DI.save()
    
    return jsonify(userAddressedCompliments), 200

@apiBP.route("/api/sendCompliment", methods=["POST"])
def sendCompliment():
    if not request.is_json:
        return "ERROR: Request body is not JSON.", 400
    
    requestBody = copy.deepcopy(request.json)
    accID = checkCredentials(requestBody)
    if accID.startswith("ERROR"):
        return accID, 401
    
    if "to" not in request.json:
        return "ERROR: Recipient not provided.", 400
    if request.json["to"] not in [DI.data["accounts"][x]["fullName"] for x in DI.data["accounts"]]:
        return "ERROR: Recipient does not exist.", 200
    if "text" not in request.json:
        return "ERROR: Compliment text not provided.", 400
    if "isAnonymous" not in request.json:
        return "ERROR: Anonymous status not provided.", 400
    
    recipientID = None
    for id in DI.data["accounts"]:
        if DI.data["accounts"][id]["fullName"] == request.json["to"]:
            recipientID = id
            break
    
    DI.data["compliments"][Universal.generateUniqueID()] = {
        "from": accID,
        "to": recipientID,
        "text": request.json["text"],
        "imgName": "sample3.jpg",
        "isAnonymous": request.json["isAnonymous"] == "True",
        "recipientAcknowledged": False,
        "datetime": datetime.datetime.now().strftime(Universal.systemWideStringDatetimeFormat)
    }
    DI.save()

    ## Send Emailer
    note = {
        "from": "Anonymous" if request.json["isAnonymous"] == "True" else DI.data["accounts"][accID]["fullName"],
        "text": request.json["text"]
    }
    Emailer.sendEmail(
        destEmail=DI.data["accounts"][recipientID]["email"],
        subject="New Compliment Received",
        altText="You have received a new compliment on KudosU! Login to the website to check it out!",
        html=render_template("emails/NewCompliment.html", note=note, homepage="http://localhost:5000/")
    )

    return "SUCCESS: Compliment sent.", 200

@apiBP.route('/api/getSentiment', methods=["POST"])
def getSentiment():
    if not request.is_json:
        return "ERROR: Request body is not JSON.", 400
    
    if "text" not in request.json:
        return "ERROR: Text not provided.", 400
    if not isinstance(request.json["text"], str):
        return "ERROR: Text is not a string.", 400
    
    textToBeAnalysed = request.json["text"].strip()
    if not textToBeAnalysed or len(textToBeAnalysed) == 0:
        return "ERROR: empty text."
    
    ## Perform sentiment analysis 
    output = sentimentfunc(textToBeAnalysed)

    if output.startswith("ERROR"):
        return output
    
    return "SUCCESS: " + output