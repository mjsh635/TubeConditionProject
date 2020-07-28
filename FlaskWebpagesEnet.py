""" This will be hosted on the RPI and provide the interface
that will start/stop conditioning, and configure the power supplies
to the correct values for the type of conditioning. This will be for
the Ethernet based supplies

To set this up, file locations need to be given for the settings file location, and the log file locations
"""

from flask import Flask, render_template, request, redirect, send_file, send_from_directory, flash
import time,datetime
import os
from MyScripts import settingsPickler, Logging_Controller, DXM, conditioning

settingsFile1 = settingsPickler.SettingsPickle(r"Z:\MiscWorkJunk\TubeCondition\settings_file.pkl")
settings = settingsFile1.read_pickle()

Logger_1 = Logging_Controller.Conditioning_Logger(r"Z:\MiscWorkJunk\TubeCondition\LogFiles_Supply1")

app = Flask(__name__)
app.secret_key = 'random string'

supply1 = DXM.DXM_Supply()
conditioner1 = conditioning.conditioning_Controller(HVSupply = supply1,Logger = Logger_1, HVSettings=settings)


conditioningStarted = False

@app.after_request
def add_header(response):
   
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

@app.route("/", methods=["GET"])
def redirect_to_main_page():
    # redirect to the main page
    return redirect("/Quick_Access")
    

@app.route("/Quick_Access", methods=["GET", "POST"])
def Home_Load():
    # Main page, loading in the required variables for the document
    if not supply1.connected:
        flash("No connection to Supply 1")
    return render_template("QuickAccess.html", settings1 = settings)
    
@app.route("/supplyConnection", methods=["GET"])
def SupplyConnect():
    supply1.try_connect()
    return str(supply1.connected)

@app.route("/hvsupplypage", methods=["GET", "POST"])
def HVSettings():
    # HVSettings page, loading in the required variables for the page
    model = supply1.model
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
    else:
        settings["maxKV"]= 0
        settings["maxMA"]= 0

    if not supply1.connected:
        flash("No connection to Supply 1, some functions will be missing")

    return render_template("HVSettings.html", settings1 = settings)

@app.route("/LogFileDownloaderPSU1", methods = ['GET'])
def downloadLog():
    # Log File Downloader, on the quicklaunch page is a button that
    # calls this function, it takes all the log files, zips them, and
    # returns the zip file for downloading
    timestamp = time.strftime("%Y_%m_%d_%H_%M_%S")
    zip_path = Logger_1.zip_files(f"All_Log_files_as_of{timestamp}", Logger_1.search_directory())
    
    return send_file(f"{zip_path}", as_attachment=True, mimetype="application/zip")

@app.route("/kvmaUpdate", methods= ["GET"])
def kvmaUpdate():
    
    # this is called when a conditioning routine is in progress to allow an updated KV MA readout to be displayed
    return f"KV :{conditioner1.currentReadKV:.2f} MA: {conditioner1.currentReadMA:.2f} Filcur: {conditioner1.currentReadFilcur:.2f}"

@app.route("/ManualXrayControl", methods = ["POST"])
def XrayONOFF():
    # xray on and off control
    compresp = ""
    # check statment for ensuring that the setpoints
    # are lower than the maximums

    if ((float(request.form["kvSet"]) <= float(settings['maxKV']) and float(request.form["kvSet"]) <= float(settings['maxTubeKV'] )) and (
    float(request.form["mASet"]) <= float(settings['maxMA']) and float(request.form["mASet"]) <= float(settings['maxTubeMA']))):

        if "Xray_On" in request.form.keys():
            # this is executed if post is for Xray on
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
            # this is executed if post is for setting KVMA
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
            # this is executed if post is for xray off
            with supply1:
                supply1.xray_off()
                while True:
                    time.sleep(1)
                    if (supply1.is_emitting()):
                        pass
                    else:
                        break

                
            Logger_1.append_to_log(f"""[Manual Xray OFF 
            {datetime.datetime.today()}]""")
            compresp = "Xrays Turned Off"
        
        elif "CurrentValues" in request.form.keys():
            # this is executed if post is for current values
            try:
                with supply1:
                    resp = supply1.read_volt_curr_filCur()
                    if supply1.is_emitting():
                        compresp = "KV: {0:.2f}, MA: {1:.2f}, FL {2:.2f}".format(resp[0],resp[1],resp[2])
                    else:
                        
                        compresp = "Xrays are OFF"
            except:
                compresp = "an error occured"
    else:
        compresp = "KV or MA higher than set Max, check HV Settings for limit. Is the right tube type chosen?"
    # display messages to used
    flash(compresp)

    return redirect("/Quick_Access")

@app.route("/updateHV", methods = ["POST", "GET"])
def HVUpdate():
    mes = ""
    if (float(request.form["condMAStart"]) <= float(request.form["condMATarget"])) and (float(request.form["condKVStart"])<= float(request.form["condKVStart"])):
        if (float(request.form["condKVTarget"]) >= settings['maxTubeKV'])  or (float(request.form["condMATarget"]) >= settings['maxTubeMA']) or (float(request.form["condKVStart"]) >= settings['maxTubeKV']) or (float(request.form["condMAStart"]) >= settings['maxTubeMA']):
            settings["filCurLim"] = request.form["filCurLim"]
            settings["filPreHeat"] = request.form["filPreHeat"]
            settings["condKVStart"] = 0
            settings["condMAStart" ]= 0
            settings["condMATarget"]= 1
            settings["condKVTarget" ]= 1
            settings["condStepDwell"]= request.form["condStepDwell"]
            settings["condAtMaxDwell"] = request.form["condAtMaxDwell"]
            settings["condPostArcDwell"]= request.form["condPostArcDwell"]
            settings["condOffDwell"]= request.form["condOffDwell"]
            settings["condStepCount"]= request.form["condStepCount"]
            mes = "KV and MA Targets set higher than tubes allowable power rating"
        else:
            settings["filCurLim"] = request.form["filCurLim"]
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
            # settings["maxKV"]= request.form["maxKV"]
            # settings["maxMA"]= request.form["maxMA"]
            mes = "Set values successfully"
    else:
        settings["filCurLim"] = request.form["filCurLim"]
        settings["filPreHeat"] = request.form["filPreHeat"]
        settings["condKVStart"] = 0
        settings["condMAStart" ]= 0
        settings["condMATarget"]= 1
        settings["condKVTarget" ]= 1
        settings["condStepDwell"]= request.form["condStepDwell"]
        settings["condAtMaxDwell"] = request.form["condAtMaxDwell"]
        settings["condPostArcDwell"]= request.form["condPostArcDwell"]
        settings["condOffDwell"]= request.form["condOffDwell"]
        settings["condStepCount"]= request.form["condStepCount"]
        mes = "KV and MA Targets set higher than tubes allowable power rating"
        mes = "KV Target and MA Target must be higher than KV Start and MA Start"

    settingsFile1.write_pickle(settings)
    flash(mes)
    return redirect("/hvsupplypage")

@app.route("/settingTubes", methods = ["POST"])
def updateTube():
    settings["tubeSNum"] = request.form["tubeSNum"]
    settings["tubeType"] = request.form["tubeType"]
    if settings["tubeType"] == '16':
        settings['maxTubeKV'] = 20
        settings['maxTubeMA'] = 4
    elif settings["tubeType"] == '16s':
        settings['maxTubeKV'] = 20
        settings['maxTubeMA'] = 2
    elif settings["tubeType"] == '32':
        settings['maxTubeKV'] = 30
        settings['maxTubeMA'] = 10
    elif settings["tubeType"] == '60':
        settings['maxTubeKV'] = 60
        settings['maxTubeMA'] = 50
    elif settings["tubeType"] == 'EMP':
        settings['maxTubeKV'] = 60
        settings['maxTubeMA'] = 50
    print(settings["tubeType"], settings['maxTubeKV'],settings['maxTubeMA'])
    Logger_1.logfile_creation(settings["tubeSNum"])
    flash("Tube type and serial number set")
    return redirect("/Quick_Access")

@app.route("/SCond", methods = ["POST"])
def Conditioning_Start_Stop():
    msg = ""
    if not supply1.connected:
        flash("No connection to Supply 1, some functions will be missing")
        return redirect("/hvsupplypage")
    else:    
        if "StartCond" in request.form.keys():
            conditioner1.start_cycle()
            settings["condStarted"] = True
            msg = "Starting Conditioning"
        elif "StopCond" in request.form.keys():
            conditioner1.stop_cycle()
            settings["condStarted"] = False
            msg = "Stopping Conditioning"
        flash(msg)
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