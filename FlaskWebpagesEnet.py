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

settingsFile1 = settingsPickler.SettingsPickle(r"Z:\MiscWorkJunk\TubeCondition\settings_file1.pkl")
settings1 = settingsFile1.read_pickle()
settingsFile2 = settingsPickler.SettingsPickle(r"Z:\MiscWorkJunk\TubeCondition\settings_file2.pkl")
settings2 = settingsFile1.read_pickle()
settingsFile3 = settingsPickler.SettingsPickle(r"Z:\MiscWorkJunk\TubeCondition\settings_file3.pkl")
settings3 = settingsFile1.read_pickle()
settingsFile4 = settingsPickler.SettingsPickle(r"Z:\MiscWorkJunk\TubeCondition\settings_file4.pkl")
settings4 = settingsFile1.read_pickle()

Logger_1 = Logging_Controller.Conditioning_Logger(r"Z:\MiscWorkJunk\TubeCondition\LogFiles")
Logger_2 = Logging_Controller.Conditioning_Logger(r"Z:\MiscWorkJunk\TubeCondition\LogFiles")
Logger_3 = Logging_Controller.Conditioning_Logger(r"Z:\MiscWorkJunk\TubeCondition\LogFiles")
Logger_4 = Logging_Controller.Conditioning_Logger(r"Z:\MiscWorkJunk\TubeCondition\LogFiles")

app = Flask(__name__)
app.secret_key = 'random string'

supply1 = DXM.DXM_Supply()
conditioner1 = conditioning.conditioning_Controller(HVSupply = supply1,Logger = Logger_1, HVSettings=settings1)
supply2 = DXM.DXM_Supply()
conditioner2 = conditioning.conditioning_Controller(HVSupply = supply2,Logger = Logger_2, HVSettings=settings2)
supply3 = DXM.DXM_Supply()
conditioner3 = conditioning.conditioning_Controller(HVSupply = supply3,Logger = Logger_3, HVSettings=settings3)
supply4 = DXM.DXM_Supply()
conditioner4 = conditioning.conditioning_Controller(HVSupply = supply4,Logger = Logger_4, HVSettings=settings4)


conditioningStarted1 = False
conditioningStarted2 = False
conditioningStarted3 = False
conditioningStarted4 = False

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
    if not supply2.connected:
        flash("No connection to Supply 2")
    if not supply3.connected:
        flash("No connection to Supply 3")
    if not supply4.connected:
        flash("No connection to Supply 4")

    return render_template("QuickAccess.html", connected1 = supply1.connected,connected2 = supply2.connected,connected3 = supply3.connected,connected4 = supply4.connected, settings1 = settings1, settings2 = settings2, settings3 = settings3 ,settings4 = settings4)
    
@app.route("/supplyConnection1", methods=["GET"])
def SupplyConnect1():
    supply1.try_connect()
    return str(supply1.connected)

@app.route("/supplyConnection2", methods=["GET"])
def SupplyConnect2():
    supply2.try_connect()
    return str(supply2.connected)

@app.route("/supplyConnection3", methods=["GET"])
def SupplyConnect3():
    supply3.try_connect()
    return str(supply3.connected)

@app.route("/supplyConnection4", methods=["GET"])
def SupplyConnect4():
    supply4.try_connect()
    return str(supply4.connected)

@app.route("/hvsupplypage", methods=["GET", "POST"])
def HVSettings():
    # HVSettings page, loading in the required variables for the page
    model1 = supply1.model
    if model1 == 'X4087':
        settings1["maxKV"]= 40
        settings1["maxMA"]= 30  
    elif model1 == 'X3481':
        settings1["maxKV"]= 30
        settings1["maxMA"]= 10
    elif model1 == 'X4911':
        settings1["maxKV"]= 40
        settings1["maxMA"]= 15
    elif model1 == 'X4313':
        settings1["maxKV"]= 30
        settings1["maxMA"]= 20
    else:
        settings1["maxKV"]= 0
        settings1["maxMA"]= 0

    model2 = supply2.model
    if model2 == 'X4087':
        settings2["maxKV"]= 40
        settings2["maxMA"]= 30  
    elif model2 == 'X3481':
        settings2["maxKV"]= 30
        settings2["maxMA"]= 10
    elif model2 == 'X4911':
        settings2["maxKV"]= 40
        settings2["maxMA"]= 15
    elif model2 == 'X4313':
        settings2["maxKV"]= 30
        settings2["maxMA"]= 20
    else:
        settings2["maxKV"]= 0
        settings2["maxMA"]= 0

    model3 = supply3.model
    if model3 == 'X4087':
        settings3["maxKV"]= 40
        settings3["maxMA"]= 30  
    elif model3 == 'X3481':
        settings3["maxKV"]= 30
        settings3["maxMA"]= 10
    elif model3 == 'X4911':
        settings3["maxKV"]= 40
        settings3["maxMA"]= 15
    elif model3 == 'X4313':
        settings3["maxKV"]= 30
        settings3["maxMA"]= 20
    else:
        settings3["maxKV"]= 0
        settings3["maxMA"]= 0

    model4 = supply4.model
    if model4 == 'X4087':
        settings4["maxKV"]= 40
        settings4["maxMA"]= 30  
    elif model4 == 'X3481':
        settings1["maxKV"]= 30
        settings1["maxMA"]= 10
    elif model4 == 'X4911':
        settings4["maxKV"]= 40
        settings4["maxMA"]= 15
    elif model4 == 'X4313':
        settings4["maxKV"]= 30
        settings4["maxMA"]= 20
    else:
        settings4["maxKV"]= 0
        settings4["maxMA"]= 0

    if not supply1.connected:
        flash("No connection to Supply 1, some functions will be missing")
    if not supply2.connected:
        flash("No connection to Supply 2, some functions will be missing")
    if not supply3.connected:
        flash("No connection to Supply 3, some functions will be missing")
    if not supply4.connected:
        flash("No connection to Supply 4, some functions will be missing")

    return render_template("HVSettings.html", settings1 = settings1, settings2 = settings2, settings3 = settings3, settings4 = settings4)

@app.route("/LogFileDownloaderAll", methods = ['GET'])
def downloadAllLog():
    # Log File Downloader, on the quicklaunch page is a button that
    # calls this function, it takes all the log files, zips them, and
    # returns the zip file for downloading
    timestamp = time.strftime("%Y_%m_%d_%H_%M_%S")
    zip_path = Logger_1.zip_files(f"All_Log_files_as_of{timestamp}", Logger_1.search_directory())
    
    return send_file(f"{zip_path}", as_attachment=True, mimetype="application/zip")

@app.route("/kvmaUpdate1", methods= ["GET"])
def kvmaUpdate1():
    
    # this is called when a conditioning routine is in progress to allow an updated KV MA readout to be displayed
    return f"KV :{conditioner1.currentReadKV:.2f} MA: {conditioner1.currentReadMA:.2f} Filcur: {conditioner1.currentReadFilcur:.2f}"
@app.route("/kvmaUpdate2", methods= ["GET"])
def kvmaUpdate2():
    
    # this is called when a conditioning routine is in progress to allow an updated KV MA readout to be displayed
    return f"KV :{conditioner2.currentReadKV:.2f} MA: {conditioner2.currentReadMA:.2f} Filcur: {conditioner2.currentReadFilcur:.2f}"
@app.route("/kvmaUpdate3", methods= ["GET"])
def kvmaUpdate3():
    
    # this is called when a conditioning routine is in progress to allow an updated KV MA readout to be displayed
    return f"KV :{conditioner3.currentReadKV:.2f} MA: {conditioner3.currentReadMA:.2f} Filcur: {conditioner3.currentReadFilcur:.2f}"
@app.route("/kvmaUpdate4", methods= ["GET"])
def kvmaUpdate4():
    
    # this is called when a conditioning routine is in progress to allow an updated KV MA readout to be displayed
    return f"KV :{conditioner4.currentReadKV:.2f} MA: {conditioner4.currentReadMA:.2f} Filcur: {conditioner4.currentReadFilcur:.2f}"

@app.route("/ManualXrayControl1", methods = ["POST"])
def XrayONOFF1():
    # xray on and off control
    compresp = ""
    # check statment for ensuring that the setpoints
    # are lower than the maximums

    if ((float(request.form["kvSet"]) <= float(settings1['maxKV']) and float(request.form["kvSet"]) <= float(settings1['maxTubeKV'] )) and (
    float(request.form["mASet"]) <= float(settings1['maxMA']) and float(request.form["mASet"]) <= float(settings1['maxTubeMA']))):

        if "Xray_On" in request.form.keys():
            # this is executed if post is for Xray on
            with supply1:
                supply1.set_filament_limit(settings1['filCurLim'])
                supply1.set_filament_preheat(settings1['filPreHeat'])
                supply1.set_voltage(request.form["kvSet"])
                supply1.set_current(request.form["mASet"])
                settings1["currKV"] = request.form["kvSet"]
                settings1["currMA"] = request.form["mASet"]
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
                settings1["currKV"] = request.form["kvSet"]
                settings1["currMA"] = request.form["mASet"]

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

@app.route("/updateHV1", methods = ["POST", "GET"])
def HVUpdate1():
    mes = ""
    if (float(request.form["condMAStart"]) <= float(request.form["condMATarget"])) and (float(request.form["condKVStart"])<= float(request.form["condKVStart"])):
        if (float(request.form["condKVTarget"]) >= settings1['maxTubeKV'])  or (float(request.form["condMATarget"]) >= settings1['maxTubeMA']) or (float(request.form["condKVStart"]) >= settings1['maxTubeKV']) or (float(request.form["condMAStart"]) >= settings1['maxTubeMA']):
            settings1["filCurLim"] = request.form["filCurLim"]
            settings1["filPreHeat"] = request.form["filPreHeat"]
            settings1["condKVStart"] = 0
            settings1["condMAStart" ]= 0
            settings1["condMATarget"]= 1
            settings1["condKVTarget" ]= 1
            settings1["condStepDwell"]= request.form["condStepDwell"]
            settings1["condAtMaxDwell"] = request.form["condAtMaxDwell"]
            settings1["condPostArcDwell"]= request.form["condPostArcDwell"]
            settings1["condOffDwell"]= request.form["condOffDwell"]
            settings1["condStepCount"]= request.form["condStepCount"]
            mes = "KV and MA Targets set higher than tubes allowable power rating"
        else:
            settings1["filCurLim"] = request.form["filCurLim"]
            settings1["filPreHeat"] = request.form["filPreHeat"]
            settings1["condKVStart"] = request.form["condKVStart"]
            settings1["condKVTarget" ]= request.form["condKVTarget"]
            settings1["condMAStart" ]= request.form["condMAStart"]
            settings1["condMATarget"]= request.form["condMATarget"]
            settings1["condStepDwell"]= request.form["condStepDwell"]
            settings1["condAtMaxDwell"] = request.form["condAtMaxDwell"]
            settings1["condPostArcDwell"]= request.form["condPostArcDwell"]
            settings1["condOffDwell"]= request.form["condOffDwell"]
            settings1["condStepCount"]= request.form["condStepCount"]
            # settings["maxKV"]= request.form["maxKV"]
            # settings["maxMA"]= request.form["maxMA"]
            mes = "Set values successfully"
    else:
        settings1["filCurLim"] = request.form["filCurLim"]
        settings1["filPreHeat"] = request.form["filPreHeat"]
        settings1["condKVStart"] = 0
        settings1["condMAStart" ]= 0
        settings1["condMATarget"]= 1
        settings1["condKVTarget" ]= 1
        settings1["condStepDwell"]= request.form["condStepDwell"]
        settings1["condAtMaxDwell"] = request.form["condAtMaxDwell"]
        settings1["condPostArcDwell"]= request.form["condPostArcDwell"]
        settings1["condOffDwell"]= request.form["condOffDwell"]
        settings1["condStepCount"]= request.form["condStepCount"]
        mes = "KV and MA Targets set higher than tubes allowable power rating"
        mes = "KV Target and MA Target must be higher than KV Start and MA Start"

    settingsFile1.write_pickle(settings1)
    flash(mes)
    return redirect("/hvsupplypage")

@app.route("/settingTubes1", methods = ["POST"])
def updateTube1():
    settings1["tubeSNum"] = request.form["tubeSNum"]
    settings1["tubeType"] = request.form["tubeType"]
    if settings1["tubeType"] == '16':
        settings1['maxTubeKV'] = 20
        settings1['maxTubeMA'] = 4
    elif settings1["tubeType"] == '16s':
        settings1['maxTubeKV'] = 20
        settings1['maxTubeMA'] = 2
    elif settings1["tubeType"] == '32':
        settings1['maxTubeKV'] = 30
        settings1['maxTubeMA'] = 10
    elif settings1["tubeType"] == '60':
        settings1['maxTubeKV'] = 60
        settings1['maxTubeMA'] = 50
    elif settings1["tubeType"] == 'EMP':
        settings1['maxTubeKV'] = 60
        settings1['maxTubeMA'] = 50
    print(settings1["tubeType"], settings1['maxTubeKV'],settings1['maxTubeMA'])
    Logger_1.logfile_creation(settings1["tubeSNum"])
    flash("Tube type and serial number set")
    return redirect("/Quick_Access")

@app.route("/settingTubes2", methods = ["POST"])
def updateTube2():
    settings2["tubeSNum"] = request.form["tubeSNum"]
    settings2["tubeType"] = request.form["tubeType"]
    if settings2["tubeType"] == '16':
        settings2['maxTubeKV'] = 20
        settings2['maxTubeMA'] = 4
    elif settings2["tubeType"] == '16s':
        settings2['maxTubeKV'] = 20
        settings2['maxTubeMA'] = 2
    elif settings2["tubeType"] == '32':
        settings2['maxTubeKV'] = 30
        settings2['maxTubeMA'] = 10
    elif settings2["tubeType"] == '60':
        settings2['maxTubeKV'] = 60
        settings2['maxTubeMA'] = 50
    elif settings2["tubeType"] == 'EMP':
        settings2['maxTubeKV'] = 60
        settings2['maxTubeMA'] = 50
    print(settings2["tubeType"], settings2['maxTubeKV'],settings2['maxTubeMA'])
    Logger_2.logfile_creation(settings2["tubeSNum"])
    flash("Tube type and serial number set")
    return redirect("/Quick_Access")

@app.route("/settingTubes3", methods = ["POST"])
def updateTube3():
    settings3["tubeSNum"] = request.form["tubeSNum"]
    settings3["tubeType"] = request.form["tubeType"]
    if settings3["tubeType"] == '16':
        settings3['maxTubeKV'] = 20
        settings3['maxTubeMA'] = 4
    elif settings3["tubeType"] == '16s':
        settings3['maxTubeKV'] = 20
        settings3['maxTubeMA'] = 2
    elif settings3["tubeType"] == '32':
        settings3['maxTubeKV'] = 30
        settings3['maxTubeMA'] = 10
    elif settings3["tubeType"] == '60':
        settings3['maxTubeKV'] = 60
        settings3['maxTubeMA'] = 50
    elif settings3["tubeType"] == 'EMP':
        settings3['maxTubeKV'] = 60
        settings3['maxTubeMA'] = 50
    print(settings3["tubeType"], settings3['maxTubeKV'],settings3['maxTubeMA'])
    Logger_3.logfile_creation(settings3["tubeSNum"])
    flash("Tube type and serial number set")
    return redirect("/Quick_Access")

@app.route("/settingTubes4", methods = ["POST"])
def updateTube4():
    settings4["tubeSNum"] = request.form["tubeSNum"]
    settings4["tubeType"] = request.form["tubeType"]
    if settings4["tubeType"] == '16':
        settings4['maxTubeKV'] = 20
        settings4['maxTubeMA'] = 4
    elif settings4["tubeType"] == '16s':
        settings4['maxTubeKV'] = 20
        settings4['maxTubeMA'] = 2
    elif settings4["tubeType"] == '32':
        settings4['maxTubeKV'] = 30
        settings4['maxTubeMA'] = 10
    elif settings4["tubeType"] == '60':
        settings4['maxTubeKV'] = 60
        settings4['maxTubeMA'] = 50
    elif settings4["tubeType"] == 'EMP':
        settings4['maxTubeKV'] = 60
        settings4['maxTubeMA'] = 50
    print(settings4["tubeType"], settings4['maxTubeKV'],settings4['maxTubeMA'])
    Logger_4.logfile_creation(settings4["tubeSNum"])
    flash("Tube type and serial number set")
    return redirect("/Quick_Access")

@app.route("/SCond1", methods = ["POST"])
def Conditioning_Start_Stop1():
    msg = ""
    if not supply1.connected:
        flash("No connection to Supply 1, some functions will be missing")
        return redirect("/hvsupplypage")
    else:    
        if "StartCond" in request.form.keys():
            conditioner1.start_cycle()
            settings1["condStarted"] = True
            msg = "Starting Conditioning"
        elif "StopCond" in request.form.keys():
            conditioner1.stop_cycle()
            settings1["condStarted"] = False
            msg = "Stopping Conditioning"
        flash(msg)
        return redirect("/hvsupplypage")

@app.route("/SCond2", methods = ["POST"])
def Conditioning_Start_Stop2():
    msg = ""
    if not supply2.connected:
        flash("No connection to Supply 2, some functions will be missing")
        return redirect("/hvsupplypage")
    else:    
        if "StartCond" in request.form.keys():
            conditioner2.start_cycle()
            settings2["condStarted"] = True
            msg = "Starting Conditioning"
        elif "StopCond" in request.form.keys():
            conditioner2.stop_cycle()
            settings2["condStarted"] = False
            msg = "Stopping Conditioning"
        flash(msg)
        return redirect("/hvsupplypage")

@app.route("/SCond3", methods = ["POST"])
def Conditioning_Start_Stop3():
    msg = ""
    if not supply3.connected:
        flash("No connection to Supply 3, some functions will be missing")
        return redirect("/hvsupplypage")
    else:    
        if "StartCond" in request.form.keys():
            conditioner3.start_cycle()
            settings3["condStarted"] = True
            msg = "Starting Conditioning"
        elif "StopCond" in request.form.keys():
            conditioner3.stop_cycle()
            settings3["condStarted"] = False
            msg = "Stopping Conditioning"
        flash(msg)
        return redirect("/hvsupplypage")

@app.route("/SCond4", methods = ["POST"])
def Conditioning_Start_Stop4():
    msg = ""
    if not supply4.connected:
        flash("No connection to Supply 4, some functions will be missing")
        return redirect("/hvsupplypage")
    else:    
        if "StartCond" in request.form.keys():
            conditioner4.start_cycle()
            settings4["condStarted"] = True
            msg = "Starting Conditioning"
        elif "StopCond" in request.form.keys():
            conditioner4.stop_cycle()
            settings4["condStarted"] = False
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