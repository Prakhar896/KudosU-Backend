import os, sys, json, datetime, copy
from flask import Blueprint, request, jsonify, redirect, url_for, render_template, session
from main import DI, Universal

apiBP = Blueprint('api', __name__)

def checkCredentials(requestBody):
    if "email" not in requestBody:
        return "ERROR: Email not provided."
    if "password" not in requestBody:
        return "ERROR: Password not provided."

    for account in DI.data["accounts"]:
        if DI.data["accounts"][account]["email"] == requestBody["email"] and DI.data["accounts"][account]["password"] == requestBody["password"]:
            return True
        
    return "ERROR: Invalid credentials."

@apiBP.route("/api/health", methods=["GET"])
def health():
    return "SUCCESS: Healthy!", 200

@apiBP.route("/api/login", methods=["POST"])
def login():
    if not request.is_json:
        return "ERROR: Request body is not JSON.", 400
    
    requestBody = copy.deepcopy(request.json)
    response = checkCredentials(requestBody)
    if response != True:
        return response, 401

    return "SUCCESS: Logged in.", 200