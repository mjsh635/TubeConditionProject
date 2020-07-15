""" This will be hosted on the RPI and provide the interface
that will start/stop conditioning, and configure the power supplies
to the correct values for the type of conditioning. This will be for
the Ethernet based supplies
"""

from flask import Flask, render_template, request, redirect, send_file, send_from_directory, flash
import time,datetime
import os
from MyScripts import Logging_Controller, DXM, settingsPickler, conditioning
Logger_1 = Logging_Controller.Conditioning_Logger(r"Z:\MiscWorkJunk\TubeCondition\LogFiles\LoggingFile0.txt")
settingsFile1 = settingsPickler.SettingsPickle(r"Z:\MiscWorkJunk\TubeCondition\settings_file.pkl")
supply1 = DXM.DXM_Supply()
app = Flask(__name__)
app.secret_key = 'random string'
settings = settingsFile1.read_pickle()
conditioner1 = conditioning.conditioning_Controller(supply1,Logger_1,settings)

# Logger_1.append_to_log(f"""[Manual KV/MA Adjustment, 
#         set target KV: {request.form["kvSet"]} 
#         set target KV: {request.form["mASet"]}
#         {datetime.datetime.today()}]""")

# class conditioning( supply, settings, logger, thread )
#   start()
#       started = true
#       return started
#   stop()
#       
#
#
#
#
@app.after_request
def add_header(response):
   
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

@app.route("/", methods=["GET"])
def redirect_to_main_page():
    return redirect("/Quick_Access")

@app.route("/Quick_Access", methods=["GET", "POST"])
def Home_Load():
    return render_template("QuickAccess.html",currKV = settings["currKV"], currMA = settings["cuurMA"])

@app.route("/hvsupplypage", methods=["GET", "POST"])
def HVSettings():
    return render_template("HVSettings.html",filcurlim = settings['filCurLim'],filpreheat = settings['filpreheat'],condKVStart = settings['condKVStart'], condKVTarget = settings['condKVTarget'],condMAStart = settings['condMAStart'], condMATarget =settings['condMATarget'],condStepDwell=settings['condStepDwell'], CondPostArcDwell = settings['CondPostArcDwell'],CondOffDwell = settings['CondOffDwell'],CondStepCount = settings['CondStepCount'])

@app.route("/LogFileDownloaderPSU1", methods = ['GET'])
def downloadLog():
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    return send_file(Logger_1.filepath, as_attachment=True,attachment_filename=("LogFile "+ timestamp + ".txt"), mimetype="text/plain")

@app.route("/ManualXrayControl", methods = ["POST"])
def XrayONOFF():
    compresp = ""
    if "Xray_On" in request.form.keys():
        with supply1:
            supply1.set_filament_limit(settings['FilCurLim'])
            supply1.set_filament_preheat(settings['FilPreHeat'])
            if supply1.is_emitting():
                supply1.set_voltage(request.form["kvSet"])
                supply1.set_current(request.form["mASet"])
                settings["currKV"] = request.form["kvSet"]
                settings["currMA"] = request.form["mASet"]
            else:
                supply1.set_voltage(request.form["kvSet"])
                supply1.set_current(request.form["mASet"])
                settings["currKV"] = request.form["kvSet"]
                settings["currMA"] = request.form["mASet"]
                supply1.xray_on()
        Logger_1.append_to_log(f"""[Manual Xray On, 
        set target KV: {request.form["kvSet"]} 
        set target KV: {request.form["mASet"]}
        {datetime.datetime.today()}]""")
        compresp = "Xrays Turned On"

    elif "Set_KVMA" in request.form.keys():
        print("setting")
        with supply1:
            supply1.set_voltage(request.form["kvSet"])
            supply1.set_current(request.form["mASet"])
            settings["currKV"] = request.form["kvSet"]
            settings["currMA"] = request.form["mASet"]
        Logger_1.append_to_log(f"""[Manual KV/MA Adjustment, 
        set target KV: {request.form["kvSet"]} 
        set target KV: {request.form["mASet"]}
        {datetime.datetime.today()}]""")
        compresp = "Successfully Set"

    elif "Xray_Off" in request.form.keys():
        with supply1:
            supply1.xray_off()
            
        Logger_1.append_to_log(f"""[Manual Xray OFF 
        {datetime.datetime.today()}]""")
        compresp = "Xrays Turned Off"
    
    elif "CurrentValues" in request.form.keys():
        try:
            with supply1:
                print(supply1.is_emitting())
                if supply1.is_emitting():
                    compresp = "KV: {0:.2f}, MA: {1:.2f}, FL {2:.2f}".format(supply1.read_voltage_out(),supply1.read_current_out(),supply1.read_filament_current_out())
                else:
                    
                    compresp = "Xrays are OFF"
        except:
            compresp = "an error occured"
    flash(compresp)
    return redirect("/Quick_Access")

@app.route("/updateHV", methods = ["POST", "GET"])
def HVUpdate():
    settings["filCurLim"] =request.form["filCurLim"]
    settings["filPreHeat"] = request.form["filPreHeat"]
    settings["condKVStart"] = request.form["condKVStart"]
    settings["condKVTarget" ]= request.form["condKVTarget"]
    settings["condMAStart" ]= request.form["condMAStart"]
    settings["condMATarget"]= request.form["condMATarget"]
    settings["condStepDwell"]= request.form["condStepDwell"]
    settings["CondPostArcDwell"]= request.form["CondPostArcDwell"]
    settings["CondOffDwell"]= request.form["CondOffDwell"]
    settings["CondStepCount"]= request.form["CondStepCount"]
    settingsFile1.write_pickle(settings)

    return redirect("/hvsupplypage")

import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
current_IP = s.getsockname()[0]
s.close()

app.templates_auto_reload = True
app.run(host=current_IP)