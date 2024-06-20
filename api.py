from flask import Blueprint, request, jsonify, redirect, url_for, render_template, session

apiBP = Blueprint('api', __name__)

@apiBP.route("/api/health", methods=["GET"])
def health():
    return "SUCCESS: Healthy!", 200