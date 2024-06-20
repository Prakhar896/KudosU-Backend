from flask import Blueprint, request, jsonify, redirect, url_for, render_template, session
from main import DI, Universal

apiBP = Blueprint('api', __name__)

def checkCredentials(requestBody):
    if "email" not in requestBody:
        return "ERROR: Email not provided."
    if "password" not in requestBody:
        return "ERROR: Password not provided."

@apiBP.route("/api/health", methods=["GET"])
def health():
    return "SUCCESS: Healthy!", 200