try:
    import urequests as requests
    import machine
    on_micropython = True
except ImportError:
    import requests
import _thread
import json
import time
import sys
from gc import collect

"""
Send CHORDS data structures to a CHORDS instance.

The JSON configuration file must contain at least:
{
      "chords_host": "chords_host.com",
      "skey": "key"
}

It is fine to include all of the configuration
needed by other modules (e.g. FromWxflow and WxflowDecode).

"""

uri_queue = []
uri_queue_lock = _thread.allocate_lock()

def sendRequests(arg):
    global uri_queue
    global uri_queue_lock
    
    while True:
        # Get a uri from the queue
        uri_queue_lock.acquire()
        if len(uri_queue):
            uri = uri_queue.pop(0)
        else:
            uri = None
        uri_queue_lock.release()

        if uri:
            uri_sent = False
            while not uri_sent:
                try:
                    # Transmit the request
                    response = requests.get(uri)
                    response.close()
                    uri_sent = True      
                    print("Sent:", uri)
                    
                except Exception as ex:
                    print (
                        "Error in ToChords.sendRequests:", 
                        str(ex.__class__.__name__),str(ex), ex.args)

        else:
            # Empty queue, sleep
            time.sleep(1)

def startSender():
    """
    Start the thread
    """
    _thread.start_new_thread(sendRequests, (None,))

def buildURI(host, chords_stuff):
    """
    {
      "inst_id": "1",
      "skey": "123456",
      "vars": {
        "at": 1511456154,
        "lcount": 0,
        "ldist": 0,
        "pres": 770.0,
        "rh": 33,
        "tdry": 13.43,
        "vbat": 3.46
      }
    }
    """
    
    uri = "http://" + host + "/measurements/url_create?"
    uri = uri + "instrument_id=" + chords_stuff["inst_id"]
    for name,value in chords_stuff["vars"].items():
        # save the timetag for later; just as convention
        if name != "at":
            var = name + "=" + str(value)
            uri = uri + "&" + var
            
    if "at" in chords_stuff["vars"]:
        unix_time = chords_stuff["vars"]["at"]
        t = time.gmtime(unix_time)
        timestamp = "{:04}-{:02}-{:02}T{:02}:{:02}:{:02}Z".format(t[0], t[1], t[2], t[3], t[4], t[5])
        uri = uri + "&at=" + timestamp
    
    if "skey" in chords_stuff:
        if chords_stuff["skey"] != "":
            uri = uri + "&" + "key=" + str(chords_stuff["skey"])
            
    return uri

def submitURI(uri, max_queue):
    uri_queue_lock.acquire()
    if len(uri_queue) > max_queue:
        print("*** uri_queue full, ignoring message")
    else:
        uri_queue.append(uri)
    uri_queue_lock.release()

if __name__ == '__main__':

    chords_json = '{\
        "inst_id": "1",\
        "skey": "123456",\
        "vars": {\
        "at": 1511459453,\
        "lcount": 0,\
        "ldist": 0,\
        "pres": 769.2000000000001,\
        "rh": 30,\
        "tdry": 13.91,\
        "vbat": 3.47\
        }\
    }'

    startSender();

    if len(sys.argv) != 2:
        print ("Usage:", sys.argv[0], "config_file")
        sys.exit(1)

    config = json.loads(open(sys.argv[1]).read())
    host   = config["chords_host"]

    chords_stuff = json.loads(chords_json)

    print (chords_stuff)
    for i in range(0,10):
        uri = buildURI(host, chords_stuff)
        submitURI(uri)

    while True:
        t = time.localtime() 
        timestamp = "{:04}-{:02}-{:02} {:02}:{:02}:{:02}".format(t[0], t[1], t[2], t[3], t[4], t[5])
        print (timestamp, "Queue length: {:05}, failures:{:06}".format(waiting(), failures()))
        time.sleep(5)


    
    
    
