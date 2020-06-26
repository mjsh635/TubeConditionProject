"""This is a simple webpage that is hosted by the 
raspberry pi. This allows me to connect my computer
to the webpage and set the power level on my Laser 
Engraver instead of having to press the manual buttons
"""
from flask import Flask, render_template, request,redirect


app = Flask(__name__)


@app.route("/test", methods=["POST"])
def printer():
    if request.method == "POST":
        print(request.form["fname"],request.form["lname"])

    return redirect("/")

@app.route("/test2", methods=["POST"])
def printeer():
    print(request.form["tname"])
    return redirect("/")

@app.route("/",methods=["GET","POST"])
def start():

    return  """<!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Set Power Level</title>
                </head>
                <body>
                    <h1>SET POWER LEVEL</h1>
                    <form action="/test" method="POST">
                        <label for="fname">First name:</label><br>
                        <input type="text" id="fname" name="fname"><br>
                        <label for="lname">Last name:</label><br>
                        <input type="text" id="lname" name="lname">
                        <input type="submit" value="do shit">
                    </form>
                    <br><br><br>

                    <form action="/test2" method="POST">
                        <input type="text" id="name" name="tname">
                        <input type="submit" value="do some other shit">
                    </form>

                </body>
                </html>
            """

# Start the webpage and set it to 192.168.0.252:8000
# this is the address of the RPI on my local network
app.run()

# from threading import Thread
# from _thread import start_new_thread
# import time

# def myWhileLoop1():
    
#     while True:
#         time.sleep(1)
#         print("this is from loop 1")

# def myWhileLoop2():
    
#     while True:
#         time.sleep(2)
#         print("this is from loop 2")

# def myWhileLoop3():
    
#     while True:
#         time.sleep(3)
#         print("this is from loop 3")

# def myWhileLoop4():
#     while True:
#         time.sleep(4)
#         print("this is from loop 4")

# t1 = Thread(target=myWhileLoop1)
# t2 = Thread(target=myWhileLoop2)
# t3 = Thread(target=myWhileLoop3)
# t4 = Thread(target=myWhileLoop4)


# t1.start()
# t2.start()
# t3.start()
# t4.start()