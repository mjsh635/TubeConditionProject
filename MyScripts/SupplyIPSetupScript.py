import sys, pathlib, time
PARENT_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(PARENT_DIR))
from MyScripts.DXM import DXM_Supply #disable=pylint(import-error)

# This script will handle 3 functions, it will read a supply and determine what it's IP is 
# should you have forgotten what it was. Lets you program the network settings of the controller to
# the settings of your choice. Lastly it will determine the IP of the supply, and revert it back to default settings.


try:
    while True:
        print("""
                ++++++++++++ Choose an option from the list ++++++++++++++

                ~ Program the supply to new settings (press p, then Enter)

                ~ Other options in development
                ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                """)

        subfunction_choice = input(""" \n Please make a choice or press Ctrl + C to exit\n""").upper()
        # First choice of which function to run
        if (subfunction_choice == "P"):
            
            # choice P was selected
            print("""
                +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

                This is the function that will handle programming the supply
                to a new IP address of your choice. If To use this function
                you are required to know the current IP address and the Port
                that the supply is using. If you do not know this information
                you can run this script again instead using the (r) subfunction.

                +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                """)            
            # choice to continue or return
            p_response1 = input("""\n Please enter "b" for back or "c" to continue \n""").upper()
            if (p_response1 == "B" or p_response1 == "C"):
                # return to main menu
                if p_response1 == "B":
                    continue

                # continue with this choice
                if p_response1 == "C":
                    print("""\n Please enter the current IP address of the Supply (ex: 192.168.1.4)""")
                    curr_IP = input()
                    print("""\n Now enter the current Port of the supply (ex: 50001)""")
                    
                    try:
                        curr_Port = int(input())
                        d = DXM_Supply(IP_address=curr_IP, port=curr_Port) 
                    except ValueError as v:
                        print("invalid port entered")
                    except Exception as e:
                        print("An unknown error has occurred: ", e)
                        break
                    if d.connected:
                        print("Found the Supply at address/port",curr_IP, curr_Port)
                        print("""\n Now enter the new IP Address""")
                        new_IP = input()
                        print("writing the new network IP to the supply.")
                        try:
                            d.write_network_settings(ip_addr=new_IP)
                        except Exception as e:
                            print("An unknown error has occured: ", e)
                            break
                        print("writing successful. Allow 30 seconds to reboot.")
                        print("please be sure to write this new address down.")
                        print(new_IP)
                        input("Press any key to continue")
                        break
                    else:
                        print("No Supply Found")
                        break

        else:
            print("Invalid response, please enter d/p/r or Ctrl + C (to quit)")
        time.sleep(1)
except KeyboardInterrupt:
    print("\n\n\nQuitting...... \nThank you !")
