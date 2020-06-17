""" This will be hosted on the RPI and provide the interface
that will start/stop conditioning, and configure the power supplies
to the correct values for the type of conditioning.
"""

from flask import Flask, render_template, request, redirect, send_file, send_from_directory
import time,datetime
import os
app = Flask(__name__)

""" When connecting to landing page "/" redirect
to the Home page"""


@app.after_request
def add_header(response):
   
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

@app.route("/", methods=["GET"])
def redirect_to_main_page():
    return redirect("/Home")


@app.route("/Home", methods=["GET", "POST"])
def Home_Load():
    return render_template("Home.html")

@app.route("/logpage", methods=["GET", "POST"])
def loggingPage():
    return render_template("LoggingPage.html")

@app.route("/hvsupplypage", methods=["GET", "POST"])
def HVSettings():
    return render_template("HVSettings.html")

@app.route("/LogFileDownloader", methods = ['GET'])
def downloadLog():
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    return send_file('z:\\MiscWorkJunk\\TubeCondition\\LogFiles\\LoggingFile.txt',as_attachment=True,attachment_filename=("LogFile "+ timestamp + ".txt"), mimetype="text/plain")

import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
current_IP = s.getsockname()[0]
s.close()

app.templates_auto_reload = True
app.run(host=current_IP,)