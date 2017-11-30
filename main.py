import machine
import os
import json
from network import WLAN
import WxflowToChords

# WxflowToChords startup. 
# Wifi configuration occurs here; so don't do it in boot.py.
#
# network.json: contains network configuration
# wx.json:      contains WxflowToChords configuration
#
# If the button on the WiPy expansion board is held during a hard reset,
# (hold long enough for entire boot to occur) the WiFi will be left configured 
# as an access point (192.168.4.1), and no other code will be run. 
# Boot this if you are having trouble syncing code from pymakr, which can
# happen if threads from WxflowToChords have been left running.
#
# If the button is not pressed, we will attempt to configure the
# wifi in station mode, and start WxflowToChords.
# The network configuration must be provided in a JSON 
# configuration file named network.json, and containing:
# {
#   "router_ip": "10.0.0.1",
#   "host_ip":   "10.0.0.100",
#   "ssid":      "wifi ssid (don't forget proper capitalization",
#   "pw":        "wifi pw"
#}

# user button on expansion board. 0 when pressed
button = machine.Pin('G17',mode=machine.Pin.IN,pull=machine.Pin.PULL_UP)

# if not pressed, use WiFi station mode.
if button():
    try:
        # Look for network configuration.
        os.stat("/flash/network.json")
        conf = json.loads(open("/flash/network.json").read())
        print ("")
        print ("network.json found.")
        print ("Starting WiPy in STA mode.")
        print ("  router:", conf["router_ip"])
        print ("    host:", conf["host_ip"])
        print ("    ssid:", conf["ssid"])
        print ("WxflowToChords will be run.")
        print ("")

        wlan = WLAN()

        if machine.reset_cause() != machine.SOFT_RESET:
            wlan.init(mode=WLAN.STA)
            # configuration below MUST match your home router settings!!
            wlan.ifconfig(config=(conf["host_ip"], '255.255.255.0', conf["router_ip"], '8.8.8.8'))

        if not wlan.isconnected():
            # change the line below to match your network ssid, security and password
            wlan.connect(conf["ssid"], auth=(WLAN.WPA2, conf["pw"]), timeout=5000)
            while not wlan.isconnected():
                machine.idle() # save power while waiting

        # !!! Start the app.
        WxflowToChords.run("wx.json")

    except OSError as e:
        print ("network.json not found")

print ("")
print ("Starting WiPy in AP mode.")
print ("WxflowToChords will not be started.")
print ("")
