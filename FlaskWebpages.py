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
    return redirect("/Quick_Access")

##reminder to change the fixed values to read previous sets
@app.route("/Quick_Access", methods=["GET", "POST"])
def Home_Load():
    return render_template("QuickAccess.html", CurrKV = 1, CurrMA = 2)

@app.route("/hvsupplypage", methods=["GET", "POST"])
def HVSettings():
    return render_template("HVSettings.html")

@app.route("/LogFileDownloaderPSU1", methods = ['GET'])
def downloadLog():
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    return send_file('z:\\MiscWorkJunk\\TubeCondition\\LogFiles\\LoggingFilePSU1.txt',as_attachment=True,attachment_filename=("LogFile "+ timestamp + ".txt"), mimetype="text/plain")

@app.route("/ManualXrayControl", methods = ["POST"])
def XrayONOFF():
    if "Xray_On" in request.form.keys():
        print("Xray turning On to: ", request.form["kvSet"], " and ", request.form["mASet"] )

    elif "Xray_Off" in request.form.keys():
        print("Xray turing off")
    

    return redirect("/Quick_Access")


import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
current_IP = s.getsockname()[0]
s.close()

app.templates_auto_reload = True
app.run(host=current_IP,)