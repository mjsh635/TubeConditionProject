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
import random

settingsFile1 = settingsPickler.SettingsPickle(r"/home/pi/Desktop/TubeConditionProject/settings_file1.pkl")
settings1 = settingsFile1.read_pickle()
settingsFile2 = settingsPickler.SettingsPickle(r"/home/pi/Desktop/TubeConditionProject/settings_file2.pkl")
settings2 = settingsFile1.read_pickle()
settingsFile3 = settingsPickler.SettingsPickle(r"/home/pi/Desktop/TubeConditionProject/settings_file3.pkl")
settings3 = settingsFile1.read_pickle()
settingsFile4 = settingsPickler.SettingsPickle(r"/home/pi/Desktop/TubeConditionProject/settings_file4.pkl")
settings4 = settingsFile1.read_pickle()

Logger_1 = Logging_Controller.Conditioning_Logger(r"/home/pi/Desktop/TubeConditionProject/LogFiles/")
Logger_3 = Logging_Controller.Conditioning_Logger(r"/home/pi/Desktop/TubeConditionProject/LogFiles/")
Logger_4 = Logging_Controller.Conditioning_Logger(r"/home/pi/Desktop/TubeConditionProject/LogFiles/")
Logger_2 = Logging_Controller.Conditioning_Logger(r"/home/pi/Desktop/TubeConditionProject/LogFiles/")

app = Flask(__name__)
app.secret_key = 'random string'

supply1 = DXM.DXM_Supply(IP_address='192.168.2.4')
conditioner1 = conditioning.conditioning_Controller(HVSupply = supply1,Logger = Logger_1, HVSettings=settings1)
supply2 = DXM.DXM_Supply(IP_address='192.168.2.5')
conditioner2 = conditioning.conditioning_Controller(HVSupply = supply2,Logger = Logger_2, HVSettings=settings2)
supply3 = DXM.DXM_Supply(IP_address='192.168.2.6')
conditioner3 = conditioning.conditioning_Controller(HVSupply = supply3,Logger = Logger_3, HVSettings=settings3)
supply4 = DXM.DXM_Supply(IP_address='192.168.2.7')
conditioner4 = conditioning.conditioning_Controller(HVSupply = supply4,Logger = Logger_4, HVSettings=settings4)


conditioningStarted1 = False
conditioningStarted2 = False
conditioningStarted3 = False
conditioningStarted4 = False



@app.after_request # done
def add_header(response):
   
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    
    return response

@app.route("/", methods=["GET"]) # done
def redirect_to_main_page():
    # redirect to the main page
    return redirect("/Quick_Access")
    

@app.route("/Quick_Access", methods=["GET", "POST"]) # done
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
    
@app.route("/ajaxSupplyConnection", methods=["POST"]) # done
def SupplyConnect():
    supply_number = request.data.decode()
    supply_number = int(supply_number)
    if supply_number == 1:
        supply1.try_connect()
        return str(supply1.connected)

    if supply_number == 2:
        supply2.try_connect()
        return str(supply2.connected)

    if supply_number == 3:
        supply3.try_connect()
        return str(supply3.connected)

    if supply_number == 4:
        supply4.try_connect()
        return str(supply4.connected)

@app.route("/hvsupplypage", methods=["GET", "POST"]) # done
def HVSettings():
    # HVSettings page, loading in the required variables for the page
    
    if not supply1.connected:
        flash("No connection to Supply 1, some functions will be missing")
    if not supply2.connected:
        flash("No connection to Supply 2, some functions will be missing")
    if not supply3.connected:
        flash("No connection to Supply 3, some functions will be missing")
    if not supply4.connected:
        flash("No connection to Supply 4, some functions will be missing")
    
    return render_template("HVSettings.html", settings1 = settings1, settings2 = settings2, settings3 = settings3, settings4 = settings4)

@app.route("/LogFileDownloaderAll", methods = ['GET']) # done
def downloadAllLog():
    # Log File Downloader, on the quicklaunch page is a button that
    # calls this function, it takes all the log files, zips them, and
    # returns the zip file for downloading
    timestamp = time.strftime("%Y_%m_%d_%H_%M_%S")
    zip_path = Logger_1.zip_files(f"All_Log_files_as_of{timestamp}")
    
    return send_file(f"{zip_path}", as_attachment=True, mimetype="application/zip")

@app.route("/ajaxKvmaUpdate", methods= ["POST"]) # Done
def kvmaUpdate():
    supplyNumber = request.data.decode()
    supplyNumber = int(supplyNumber)
    if supplyNumber == 1:
        return f"KV :{conditioner1.currentReadKV:.2f} MA: {conditioner1.currentReadMA:.2f} Filcur: {conditioner1.currentReadFilcur:.2f}"
    if supplyNumber == 2:
        return f"KV :{conditioner2.currentReadKV:.2f} MA: {conditioner2.currentReadMA:.2f} Filcur: {conditioner2.currentReadFilcur:.2f}"
    if supplyNumber == 3:
        return f"KV :{conditioner3.currentReadKV:.2f} MA: {conditioner3.currentReadMA:.2f} Filcur: {conditioner3.currentReadFilcur:.2f}"
    if supplyNumber == 4:
        return f"KV :{conditioner4.currentReadKV:.2f} MA: {conditioner4.currentReadMA:.2f} Filcur: {conditioner4.currentReadFilcur:.2f}"
    # this is called when a conditioning routine is in progress to allow an updated KV MA readout to be displayed

@app.route("/ajaxXrayOff", methods = ["POST"]) # Done
def xrayOff():
    supply_number = request.data.decode()
    supply_number = int(supply_number)

    if supply_number == 1:
        if not supply1.connected:
            return "Supply 1 is not connected"

        Logger_1.append_to_log(f"""[Manual Xray OFF 
            {datetime.datetime.today()}]""")
        supply1.xray_off()
        return "Supply 1 Requested Off"
    if supply_number == 2:
        if not supply2.connected:
            return "Supply 2 is not connected"

        Logger_2.append_to_log(f"""[Manual Xray OFF 
            {datetime.datetime.today()}]""")
        supply2.xray_off()
        return "Supply 2 Requested Off"
    if supply_number == 3:
        if not supply3.connected:
            return "Supply 3 is not connected"

        Logger_3.append_to_log(f"""[Manual Xray OFF 
            {datetime.datetime.today()}]""")
        supply3.xray_off()
        return "Supply 3 Requested Off"
    if supply_number == 4:
        if not supply4.connected:
            return "Supply 4 is not connected"

        Logger_4.append_to_log(f"""[Manual Xray OFF 
            {datetime.datetime.today()}]""")
        supply4.xray_off()
        return "Supply 4 Requested Off"

@app.route("/ajaxXrayOn", methods=["POST"]) # Done
def xrayOn():
    supply_number = request.form["supplyNumber"]
    supply_number = int(supply_number)
    if supply_number == 1:
        if not supply1.connected:
            return "Supply 1 is not connected"

        if ((float(request.form["kvSet"]) <= float(settings1['maxKV']) and float(request.form["kvSet"]) <= float(settings1['maxTubeKV'] )) and (
        float(request.form["mASet"]) <= float(settings1['maxMA']) and float(request.form["mASet"]) <= float(settings1['maxTubeMA']))):

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

            return "Xrays Turned On"
        else:
            return "KV or MA higher than set Max, check HV Settings for limit. Is the right tube type chosen?"


    if supply_number == 2:
        if not supply2.connected:
            return "Supply 2 is not connected"

        if ((float(request.form["kvSet"]) <= float(settings2['maxKV']) and float(request.form["kvSet"]) <= float(settings2['maxTubeKV'] )) and (
        float(request.form["mASet"]) <= float(settings2['maxMA']) and float(request.form["mASet"]) <= float(settings2['maxTubeMA']))):

            supply2.set_filament_limit(settings2['filCurLim'])
            supply2.set_filament_preheat(settings2['filPreHeat'])
            supply2.set_voltage(request.form["kvSet"])
            supply2.set_current(request.form["mASet"])
            settings2["currKV"] = request.form["kvSet"]
            settings2["currMA"] = request.form["mASet"]
            if not supply2.is_emitting():
                supply2.xray_on()

            Logger_2.append_to_log(f"""[Manual Xray On, 
            set target KV: {request.form["kvSet"]} 
            set target KV: {request.form["mASet"]}
            {datetime.datetime.today()}]""")

            return "Xrays Turned On with Supply 2"
        else:
            return "KV or MA higher than set Max, check HV Settings for limit. Is the right tube type chosen?"

    if supply_number == 3:
        if not supply3.connected:
            return "Supply 3 is not connected"
        
        if ((float(request.form["kvSet"]) <= float(settings3['maxKV']) and float(request.form["kvSet"]) <= float(settings3['maxTubeKV'] )) and (
        float(request.form["mASet"]) <= float(settings3['maxMA']) and float(request.form["mASet"]) <= float(settings3['maxTubeMA']))):

            supply3.set_filament_limit(settings3['filCurLim'])
            supply3.set_filament_preheat(settings3['filPreHeat'])
            supply3.set_voltage(request.form["kvSet"])
            supply3.set_current(request.form["mASet"])
            settings3["currKV"] = request.form["kvSet"]
            settings3["currMA"] = request.form["mASet"]
            if not supply3.is_emitting():
                supply3.xray_on()

            Logger_3.append_to_log(f"""[Manual Xray On, 
            set target KV: {request.form["kvSet"]} 
            set target KV: {request.form["mASet"]}
            {datetime.datetime.today()}]""")

            return "Xrays Turned On with Supply 3"

        else:
            return "KV or MA higher than set Max, check HV Settings for limit. Is the right tube type chosen?"

    if supply_number == 4:
        if not supply4.connected:
            return "Supply 4 is not connected"
        
        if ((float(request.form["kvSet"]) <= float(settings4['maxKV']) and float(request.form["kvSet"]) <= float(settings4['maxTubeKV'] )) and (
        float(request.form["mASet"]) <= float(settings4['maxMA']) and float(request.form["mASet"]) <= float(settings4['maxTubeMA']))):
        
            supply4.set_filament_limit(settings4['filCurLim'])
            supply4.set_filament_preheat(settings4['filPreHeat'])
            supply4.set_voltage(request.form["kvSet"])
            supply4.set_current(request.form["mASet"])
            settings4["currKV"] = request.form["kvSet"]
            settings4["currMA"] = request.form["mASet"]
            if not supply4.is_emitting():
                supply4.xray_on()

            Logger_4.append_to_log(f"""[Manual Xray On, 
            set target KV: {request.form["kvSet"]} 
            set target KV: {request.form["mASet"]}
            {datetime.datetime.today()}]""")

            return "Xrays Turned On with Supply 4"
            
        else:
            return "KV or MA higher than set Max, check HV Settings for limit. Is the right tube type chosen?"

@app.route("/ajaxGetReadouts", methods=["POST"]) # Done
def GetReadouts():
    supply_number = request.data.decode()
    supply_number = int(supply_number)
    if supply_number == 1:
        if not supply1.connected:
            return "Supply 1 is not connected"
        return  "KV: {0:.2f}, MA: {1:.2f}, FL {2:.2f}".format(conditioner1.currentReadKV,conditioner1.currentReadMA,conditioner1.currentReadFilcur)
        

    if supply_number == 2:
        if not supply2.connected:
            return "Supply 2 is not connected"

        return  "KV: {0:.2f}, MA: {1:.2f}, FL {2:.2f}".format(conditioner2.currentReadKV,conditioner2.currentReadMA,conditioner2.currentReadFilcur)
        

    if supply_number == 3:
        if not supply3.connected:
            return "Supply 3 is not connected"

       
        return  "KV: {0:.2f}, MA: {1:.2f}, FL {2:.2f}".format(conditioner3.currentReadKV,conditioner3.currentReadMA,conditioner3.currentReadFilcur)
        

    if supply_number == 4:
        if not supply4.connected:
            return "Supply 4 is not connected"
        return  "KV: {0:.2f}, MA: {1:.2f}, FL {2:.2f}".format(conditioner4.currentReadKV,conditioner4.currentReadMA,conditioner4.currentReadFilcur)
        
    return "error, No_Supply_Condition_Statement"
@app.route("/ajaxSetKVMA", methods=["POST"]) # Done
def SetKVMA():
    supply_number =  request.form["supplyNumber"]
    supply_number = int(supply_number)
    print(request.form["kvSet"],request.form["mASet"])

    if supply_number == 1:
        if not supply1.connected:
            return "Supply 1 is not connected"
        if ((float(request.form["kvSet"]) <= float(settings1['maxKV']) and float(request.form["kvSet"]) <= float(settings1['maxTubeKV'] )) and (
        float(request.form["mASet"]) <= float(settings1['maxMA']) and float(request.form["mASet"]) <= float(settings1['maxTubeMA']))):
            supply1.set_voltage(request.form["kvSet"])
            supply1.set_current(request.form["mASet"])
            settings1["currKV"] = request.form["kvSet"]
            settings1["currMA"] = request.form["mASet"]

            Logger_1.append_to_log(f"""[Manual KV/MA Adjustment, 
            set target KV: {request.form["kvSet"]} 
            set target KV: {request.form["mASet"]}
            {datetime.datetime.today()}]""")

            return "Set the values on Supply 1"
        else:
            return "KV or MA higher than set Max, check HV Settings for limit. Is the right tube type chosen?"

    if supply_number == 2:
        if not supply2.connected:
            return "Supply 2 is not connected"

        if ((float(request.form["kvSet"]) <= float(settings2['maxKV']) and float(request.form["kvSet"]) <= float(settings2['maxTubeKV'] )) and (
        float(request.form["mASet"]) <= float(settings2['maxMA']) and float(request.form["mASet"]) <= float(settings2['maxTubeMA']))):

            supply2.set_voltage(request.form["kvSet"])
            supply2.set_current(request.form["mASet"])
            settings2["currKV"] = request.form["kvSet"]
            settings2["currMA"] = request.form["mASet"]

            Logger_2.append_to_log(f"""[Manual KV/MA Adjustment, 
            set target KV: {request.form["kvSet"]} 
            set target KV: {request.form["mASet"]}
            {datetime.datetime.today()}]""")

            return "Set the values on Supply 2"

        else:
                return "KV or MA higher than set Max, check HV Settings for limit. Is the right tube type chosen?"

    if supply_number == 3:
        if not supply3.connected:
            return "Supply 3 is not connected"
        
        if ((float(request.form["kvSet"]) <= float(settings3['maxKV']) and float(request.form["kvSet"]) <= float(settings3['maxTubeKV'] )) and (
        float(request.form["mASet"]) <= float(settings3['maxMA']) and float(request.form["mASet"]) <= float(settings3['maxTubeMA']))):    

            supply3.set_voltage(request.form["kvSet"])
            supply3.set_current(request.form["mASet"])
            settings3["currKV"] = request.form["kvSet"]
            settings3["currMA"] = request.form["mASet"]

            Logger_3.append_to_log(f"""[Manual KV/MA Adjustment, 
            set target KV: {request.form["kvSet"]} 
            set target KV: {request.form["mASet"]}
            {datetime.datetime.today()}]""")

            return "Set the values on Supply 3"
        else:
                return "KV or MA higher than set Max, check HV Settings for limit. Is the right tube type chosen?"

    if supply_number == 4:
        if not supply4.connected:
            return "Supply 4 is not connected"
    
        if ((float(request.form["kvSet"]) <= float(settings4['maxKV']) and float(request.form["kvSet"]) <= float(settings4['maxTubeKV'] )) and (
        float(request.form["mASet"]) <= float(settings4['maxMA']) and float(request.form["mASet"]) <= float(settings4['maxTubeMA']))):
        
            supply4.set_voltage(request.form["kvSet"])
            supply4.set_current(request.form["mASet"])
            settings4["currKV"] = request.form["kvSet"]
            settings4["currMA"] = request.form["mASet"]

            Logger_4.append_to_log(f"""[Manual KV/MA Adjustment, 
            set target KV: {request.form["kvSet"]} 
            set target KV: {request.form["mASet"]}
            {datetime.datetime.today()}]""")

            return "Set the values on Supply 4"
        else:
            return "KV or MA higher than set Max, check HV Settings for limit. Is the right tube type chosen?"

@app.route("/ajaxUpdateHV", methods = ["POST", "GET"]) # Done
def HVUpdate1():
    supply_number =  request.form["supplyNumber"]
    supply_number = int(supply_number)
    if supply_number == 1:  
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
                settingsFile1.write_pickle(settings1)
                return "KV and MA Targets set higher than tubes allowable power rating"
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
                settingsFile1.write_pickle(settings1)
                return "Set values successfully"
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
            settingsFile1.write_pickle(settings1)
            return """KV and MA Targets set higher than tubes allowable power rating and KV Target and MA Target must be higher than KV Start and MA Start"""
        
        return "settings have been set on Supply 1"
    if supply_number == 2:  
        if (float(request.form["condMAStart"]) <= float(request.form["condMATarget"])) and (float(request.form["condKVStart"])<= float(request.form["condKVStart"])):
            if (float(request.form["condKVTarget"]) >= settings2['maxTubeKV'])  or (float(request.form["condMATarget"]) >= settings2['maxTubeMA']) or (float(request.form["condKVStart"]) >= settings2['maxTubeKV']) or (float(request.form["condMAStart"]) >= settings2['maxTubeMA']):
                settings2["filCurLim"] = request.form["filCurLim"]
                settings2["filPreHeat"] = request.form["filPreHeat"]
                settings2["condKVStart"] = 0
                settings2["condMAStart" ]= 0
                settings2["condMATarget"]= 1
                settings2["condKVTarget" ]= 1
                settings2["condStepDwell"]= request.form["condStepDwell"]
                settings2["condAtMaxDwell"] = request.form["condAtMaxDwell"]
                settings2["condPostArcDwell"]= request.form["condPostArcDwell"]
                settings2["condOffDwell"]= request.form["condOffDwell"]
                settings2["condStepCount"]= request.form["condStepCount"]
                settingsFile2.write_pickle(settings2)
                return "KV and MA Targets set higher than tubes allowable power rating"
            else:
                settings2["filCurLim"] = request.form["filCurLim"]
                settings2["filPreHeat"] = request.form["filPreHeat"]
                settings2["condKVStart"] = request.form["condKVStart"]
                settings2["condKVTarget" ]= request.form["condKVTarget"]
                settings2["condMAStart" ]= request.form["condMAStart"]
                settings2["condMATarget"]= request.form["condMATarget"]
                settings2["condStepDwell"]= request.form["condStepDwell"]
                settings2["condAtMaxDwell"] = request.form["condAtMaxDwell"]
                settings2["condPostArcDwell"]= request.form["condPostArcDwell"]
                settings2["condOffDwell"]= request.form["condOffDwell"]
                settings2["condStepCount"]= request.form["condStepCount"]
                settingsFile2.write_pickle(settings2)
                return "Set values successfully"
        else:
            settings2["filCurLim"] = request.form["filCurLim"]
            settings2["filPreHeat"] = request.form["filPreHeat"]
            settings2["condKVStart"] = 0
            settings2["condMAStart" ]= 0
            settings2["condMATarget"]= 1
            settings2["condKVTarget" ]= 1
            settings2["condStepDwell"]= request.form["condStepDwell"]
            settings2["condAtMaxDwell"] = request.form["condAtMaxDwell"]
            settings2["condPostArcDwell"]= request.form["condPostArcDwell"]
            settings2["condOffDwell"]= request.form["condOffDwell"]
            settings2["condStepCount"]= request.form["condStepCount"]
            settingsFile2.write_pickle(settings2)
            return """KV and MA Targets set higher than tubes allowable power rating and KV Target and MA Target must be higher than KV Start and MA Start"""
        
        return "settings have been set on Supply 2"
    if supply_number == 3:
        if (float(request.form["condMAStart"]) <= float(request.form["condMATarget"])) and (float(request.form["condKVStart"])<= float(request.form["condKVStart"])):
            if (float(request.form["condKVTarget"]) >= settings3['maxTubeKV'])  or (float(request.form["condMATarget"]) >= settings3['maxTubeMA']) or (float(request.form["condKVStart"]) >= settings3['maxTubeKV']) or (float(request.form["condMAStart"]) >= settings3['maxTubeMA']):
                settings3["filCurLim"] = request.form["filCurLim"]
                settings3["filPreHeat"] = request.form["filPreHeat"]
                settings3["condKVStart"] = 0
                settings3["condMAStart" ]= 0
                settings3["condMATarget"]= 1
                settings3["condKVTarget" ]= 1
                settings3["condStepDwell"]= request.form["condStepDwell"]
                settings3["condAtMaxDwell"] = request.form["condAtMaxDwell"]
                settings3["condPostArcDwell"]= request.form["condPostArcDwell"]
                settings3["condOffDwell"]= request.form["condOffDwell"]
                settings3["condStepCount"]= request.form["condStepCount"]
                settingsFile3.write_pickle(settings3)
                return "KV and MA Targets set higher than tubes allowable power rating"
            else:
                settings3["filCurLim"] = request.form["filCurLim"]
                settings3["filPreHeat"] = request.form["filPreHeat"]
                settings3["condKVStart"] = request.form["condKVStart"]
                settings3["condKVTarget" ]= request.form["condKVTarget"]
                settings3["condMAStart" ]= request.form["condMAStart"]
                settings3["condMATarget"]= request.form["condMATarget"]
                settings3["condStepDwell"]= request.form["condStepDwell"]
                settings3["condAtMaxDwell"] = request.form["condAtMaxDwell"]
                settings3["condPostArcDwell"]= request.form["condPostArcDwell"]
                settings3["condOffDwell"]= request.form["condOffDwell"]
                settings3["condStepCount"]= request.form["condStepCount"]
                settingsFile3.write_pickle(settings3)
                return "Set values successfully"
        else:
            settings3["filCurLim"] = request.form["filCurLim"]
            settings3["filPreHeat"] = request.form["filPreHeat"]
            settings3["condKVStart"] = 0
            settings3["condMAStart" ]= 0
            settings3["condMATarget"]= 1
            settings3["condKVTarget" ]= 1
            settings3["condStepDwell"]= request.form["condStepDwell"]
            settings3["condAtMaxDwell"] = request.form["condAtMaxDwell"]
            settings3["condPostArcDwell"]= request.form["condPostArcDwell"]
            settings3["condOffDwell"]= request.form["condOffDwell"]
            settings3["condStepCount"]= request.form["condStepCount"]
            settingsFile3.write_pickle(settings3)
            return """KV and MA Targets set higher than tubes allowable power rating and KV Target and MA Target must be higher than KV Start and MA Start"""
        
        return "settings have been set on Supply 3"
    if supply_number == 4:
        if (float(request.form["condMAStart"]) <= float(request.form["condMATarget"])) and (float(request.form["condKVStart"])<= float(request.form["condKVStart"])):
            if (float(request.form["condKVTarget"]) >= settings4['maxTubeKV'])  or (float(request.form["condMATarget"]) >= settings4['maxTubeMA']) or (float(request.form["condKVStart"]) >= settings4['maxTubeKV']) or (float(request.form["condMAStart"]) >= settings4['maxTubeMA']):
                settings4["filCurLim"] = request.form["filCurLim"]
                settings4["filPreHeat"] = request.form["filPreHeat"]
                settings4["condKVStart"] = 0
                settings4["condMAStart" ]= 0
                settings4["condMATarget"]= 1
                settings4["condKVTarget" ]= 1
                settings4["condStepDwell"]= request.form["condStepDwell"]
                settings4["condAtMaxDwell"] = request.form["condAtMaxDwell"]
                settings4["condPostArcDwell"]= request.form["condPostArcDwell"]
                settings4["condOffDwell"]= request.form["condOffDwell"]
                settings4["condStepCount"]= request.form["condStepCount"]
                settingsFile4.write_pickle(settings4)
                return "KV and MA Targets set higher than tubes allowable power rating"
            else:
                settings4["filCurLim"] = request.form["filCurLim"]
                settings4["filPreHeat"] = request.form["filPreHeat"]
                settings4["condKVStart"] = request.form["condKVStart"]
                settings4["condKVTarget" ]= request.form["condKVTarget"]
                settings4["condMAStart" ]= request.form["condMAStart"]
                settings4["condMATarget"]= request.form["condMATarget"]
                settings4["condStepDwell"]= request.form["condStepDwell"]
                settings4["condAtMaxDwell"] = request.form["condAtMaxDwell"]
                settings4["condPostArcDwell"]= request.form["condPostArcDwell"]
                settings4["condOffDwell"]= request.form["condOffDwell"]
                settings4["condStepCount"]= request.form["condStepCount"]
                settingsFile4.write_pickle(settings4)
                return "Set values successfully"
        else:
            settings4["filCurLim"] = request.form["filCurLim"]
            settings4["filPreHeat"] = request.form["filPreHeat"]
            settings4["condKVStart"] = 0
            settings4["condMAStart" ]= 0
            settings4["condMATarget"]= 1
            settings4["condKVTarget" ]= 1
            settings4["condStepDwell"]= request.form["condStepDwell"]
            settings4["condAtMaxDwell"] = request.form["condAtMaxDwell"]
            settings4["condPostArcDwell"]= request.form["condPostArcDwell"]
            settings4["condOffDwell"]= request.form["condOffDwell"]
            settings4["condStepCount"]= request.form["condStepCount"]
            settingsFile4.write_pickle(settings4)
            return """KV and MA Targets set higher than tubes allowable power rating and KV Target and MA Target must be higher than KV Start and MA Start"""
        
        return "settings have been set on Supply 4"


@app.route("/ajaxSettingTubes", methods = ["POST"]) # Done
def updateTube():
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

    supplyNumber = int(request.form["supplyNumber"])
    if supplyNumber == 1:
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

        Logger_1.logfile_creation(settings1["tubeSNum"])
        return "Set Supply 1 Tubes"
    if supplyNumber == 2:
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
        Logger_2.logfile_creation(settings2["tubeSNum"])
        return "Set Supply 2 Tubes"
    if supplyNumber == 3:
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
        Logger_3.logfile_creation(settings3["tubeSNum"])
        return "Set Supply 3 Tubes"
    if supplyNumber == 4:
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
        Logger_4.logfile_creation(settings4["tubeSNum"])
        return "Set Supply 4 Tubes"
    return "The fields were left blank"

@app.route("/ajaxCondStart", methods = ["POST"]) # Done
def Conditioning_Start():
    supply_number = request.data.decode()
    supply_number = int(supply_number)
    if supply_number == 1:
        if not supply1.connected:
            return "Supply 1 is not connected"
        else:    
            conditioner1.start_cycle()
            settings1["condStarted"] = True
            return "Condition Started on Supply 1"

    if supply_number == 2:
        if not supply2.connected:
            return "Supply 2 is not connected"
        else:    
            conditioner2.start_cycle()
            settings2["condStarted"] = True
            return "Condition Started on Supply 2"

    if supply_number == 3:
        if not supply3.connected:
            return "Supply 3 is not connected"
        else:    
            conditioner3.start_cycle()
            settings3["condStarted"] = True
            return "Condition Started on Supply 3"

    if supply_number == 4:
        if not supply4.connected:
            return "Supply 4 is not connected"
        else:    
            conditioner4.start_cycle()
            settings4["condStarted"] = True
            return "Condition Started on Supply 4"

@app.route("/ajaxCondStop", methods = ["POST"]) # Done
def Conditioning_Stop():
    supply_number = request.data.decode()
    supply_number = int(supply_number)
    if supply_number == 1:
        if not supply1.connected:
            return "Supply 1 is not connected"
        else:    
            conditioner1.stop_cycle()
            settings1["condStarted"] = False
            return "Condition Stopped on Supply 1"

    if supply_number == 2:
        if not supply2.connected:
            return "Supply 2 is not connected"
        else:    
            conditioner2.stop_cycle()
            settings2["condStarted"] = False
            return "Condition Stopped on Supply 2"

    if supply_number == 3:
        if not supply3.connected:
            return "Supply 3 is not connected"
        else:    
            conditioner3.stop_cycle()
            settings3["condStarted"] = False
            return "Condition Stopped on Supply 3"

    if supply_number == 4:
        if not supply4.connected:
            return "Supply 4 is not connected"
        else:    
            conditioner4.stop_cycle()
            settings4["condStarted"] = False
            return "Condition Stopped on Supply 4"

@app.route("/ajaxGraphValues", methods = ["POST"]) # Unused
def GraphValues():
    # supply_number = request.data.decode()
    # supply_number = int(supply_number)
    # if supply_number == 1:
    #     voltData = conditioner1.VoltageOverTime
    #     currData = conditioner1.CurrentOverTime
    #     filData =  conditioner1.FilamentOverTime
    #     data = [voltData,currData,filData]
    #     return data
    # if supply_number == 2:
    #     voltData = conditioner2.VoltageOverTime
    #     currData = conditioner2.CurrentOverTime
    #     filData =  conditioner2.FilamentOverTime
    #     data = [voltData,currData,filData]
    #     return data
    # if supply_number == 3:
    #     voltData = conditioner3.VoltageOverTime
    #     currData = conditioner3.CurrentOverTime
    #     filData =  conditioner3.FilamentOverTime
    #     data = [voltData,currData,filData]
    #     return data
    # if supply_number == 4:
        # voltData = conditioner4.VoltageOverTime
        # currData = conditioner4.CurrentOverTime
        # filData =  conditioner4.FilamentOverTime
        # data = [voltData,currData,filData]
        # return data
    data = {"voltData":{1:1},"currData":{2:2},"filData":{3:3}}
    return data    
#done
def get_IP(): 
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    IP = s.getsockname()[0]
    s.close()
    return IP


app.templates_auto_reload = True
app.run(get_IP(), port=5000)