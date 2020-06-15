""" This will be hosted on the RPI and provide the interface
that will start/stop conditioning, and configure the power supplies
to the correct values for the type of conditioning.
"""

from flask import Flask, render_template, request, redirect
app = Flask(__name__)


""" When connecting to landing page "/" redirect
to the Home page"""
@app.route("/", methods=["GET"])
def redirect_to_main_page():
    return redirect("/Home")

""" The Home page will consist of navigation buttons
to bring the user to various other function screens
"""
@app.route("/Home", methods=["GET", "POST"])
def Home_Load():
    return render_template("Home.html")

@app.route("/Status", methods=["GET", "POST"])
def Status_Load():
    return render_template("Status.html")

@app.route("/Conditioning", methods=["GET", "POST"])
def conditioning_Load():
    return render_template("Conditioning.html")

@app.route("/HVSetup", methods=["GET", "POST"])
def setup_Load():
    return render_template("HVSetup.html")

app.run(debug=True,host='193.168.1.21')