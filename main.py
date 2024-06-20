import os, sys, json, datetime
from flask import Flask, request, jsonify, redirect, url_for, render_template, session
from dotenv import load_dotenv
load_dotenv()

if True in [x not in os.environ for x in ["SERVER_PORT"]]:
    print("Please set all required environment variables in .env file.")
    sys.exit(1)

app = Flask(__name__)

@app.route('/')
def index():
    return "Welcome to KudosU Backend Server."

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=os.environ["SERVER_PORT"])