""" This will be hosted on the RPI and provide the interface
that will start/stop conditioning, and configure the power supplies
to the correct values for the type of conditioning. This will be for
the Ethernet based supplies
"""

from flask import Flask, render_template, request, redirect, send_file, send_from_directory, flash
import time,datetime
import os
from MyScripts import Logging_Controller, DXM, settingsPickler, conditioning

settingsFile1 = settingsPickler.SettingsPickle(r"Z:\MiscWorkJunk\TubeCondition\settings_file.pkl")
supply1 = DXM.DXM_Supply()
Logger_1 = Logging_Controller.Conditioning_Logger(r"Z:\MiscWorkJunk\TubeCondition\LogFiles_Supply1", supply=supply1.model)
app = Flask(__name__)
app.secret_key = 'random string'
settings = settingsFile1.read_pickle()
conditioner1 = conditioning.conditioning_Controller(supply1,Logger_1,settings)

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
    print(conditioner1.CondStarted)
    return render_template("QuickAccess.html", currKV = settings["currKV"], currMA = settings["currMA"], grayOut = conditioner1.CondStarted, tubeSNum = settings["tubeSNum"])
    

@app.route("/hvsupplypage", methods=["GET", "POST"])
def HVSettings():
    with supply1:
        model = supply1.read_model_type()[1]
    if model == 'X4087':
        settings["maxKV"]= 40
        settings["maxMA"]= 30  
    elif model == 'X3481':
        settings["maxKV"]= 30
        settings["maxMA"]= 10
    elif model == 'X4911':
        settings["maxKV"]= 40
        settings["maxMA"]= 15
    elif model == 'X4313':
        settings["maxKV"]= 30
        settings["maxMA"]= 20
    return render_template("HVSettings.html",filCurLim = settings['filCurLim'],filPreHeat = settings['filPreHeat'],condKVStart = settings['condKVStart'], condKVTarget = settings['condKVTarget'],condMAStart = settings['condMAStart'], condMATarget =settings['condMATarget'],condStepDwell=settings['condStepDwell'], condPostArcDwell = settings['condPostArcDwell'],condOffDwell = settings['condOffDwell'],condStepCount = settings['condStepCount'], maxKV = settings['maxKV'], maxMA = settings['maxMA'], condAtMaxDwell = settings["condAtMaxDwell"])

@app.route("/LogFileDownloaderPSU1", methods = ['GET'])
def downloadLog():
    timestamp = time.strftime("%Y_%m_%d_%H_%M_%S")
    zip_path = Logger_1.zip_files(f"All_Log_files_as_of{timestamp}",Logger_1.search_directory())
    
    return send_file(f"{zip_path}", as_attachment=True, mimetype="application/zip")

@app.route("/ManualXrayControl", methods = ["POST"])
def XrayONOFF():
    compresp = ""

    if (float(request.form["kvSet"]) <= float(settings['maxKV']) and
    float(request.form["mASet"]) <= float(settings['maxMA'])):

        if "Xray_On" in request.form.keys():
            with supply1:
                supply1.set_filament_limit(settings['filCurLim'])
                supply1.set_filament_preheat(settings['filPreHeat'])
                supply1.set_voltage(request.form["kvSet"])
                supply1.set_current(request.form["mASet"])
                settings["currKV"] = request.form["kvSet"]
                settings["currMA"] = request.form["mASet"]
                if not supply1.is_emitting():
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
    else:
        compresp = "KV or MA higher than set Max, check HV Settings for limit"

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
    settings["condAtMaxDwell"] = request.form["condAtMaxDwell"]
    settings["condPostArcDwell"]= request.form["condPostArcDwell"]
    settings["condOffDwell"]= request.form["condOffDwell"]
    settings["condStepCount"]= request.form["condStepCount"]
    settings["maxKV"]= request.form["maxKV"]
    settings["maxMA"]= request.form["maxMA"]
    settingsFile1.write_pickle(settings)

    return redirect("/hvsupplypage")

@app.route("/settingTubes", methods = ["POST"])
def updateTube():
    settings["tubeSNum"] = request.form["tubeSNum"]
    Logger_1.logfile_creation(settings["tubeSNum"])
    return redirect("/Quick_Access")

@app.route("/SCond", methods = ["POST"])
def Conditioning_Start_Stop():
    if "StartCond" in request.form.keys():
        conditioner1.start_cycle()
    elif "StopCond" in request.form.keys():
        conditioner1.stop_cycle()
    return redirect("/hvsupplypage")

def get_IP():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    IP = s.getsockname()[0]
    s.close()
    return IP


app.templates_auto_reload = True
app.run(host=get_IP())