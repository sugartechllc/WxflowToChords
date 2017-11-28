try:
    import urequests as requests
    on_micropython = True
except ImportError:
    import requests
    on_micropython = False
import _thread
import json
import time
import sys

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
uri_send_failures = 0
uri_queue_lock = _thread.allocate_lock()

#####################################################################
def sendRequests(timeout):
    global uri_queue
    global uri_send_failures
    global uri_queue_lock
    
    q_remain = 0
    while True:
        try:
            # Get a uri from the queue
            uri_queue_lock.acquire()
            if len(uri_queue):
                uri = uri_queue.pop(0)
            else:
                uri = ""
            uri_queue_lock.release()
            
            # Transmit the request
            if len(uri) > 0:
                if not on_micropython:
                    response = requests.get(uri, timeout=timeout)
                else:
                    response = requests.get(uri)
            
            # How many more messages avaiable?
            uri_queue_lock.acquire()
            q_remain = len(uri_queue)
            uri_queue_lock.release()
            # Sleep if the queue is empty
            if q_remain == 0:
                time.sleep(1)
        except Exception as e:
            uri_queue_lock.acquire()
            uri_send_failures = uri_send_failures + 1
            uri_queue_lock.release()
            print ("Error in sendRequests:", e)

            
#####################################################################
def startSender(timeout):
    _thread.start_new_thread(sendRequests, (timeout,))
    
#####################################################################
def failures():
    global uri_send_failures
    global uri_queue_lock
    
    uri_queue_lock.acquire()
    n = uri_send_failures
    uri_send_failures = 0
    uri_queue_lock.release()
    
    return n

#####################################################################
def waiting():
    global uri_queue
    global uri_queue_lock
    
    uri_queue_lock.acquire()
    n = len(uri_queue)
    uri_queue_lock.release()
    
    return n

#####################################################################
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

#####################################################################
def submitURI(uri):
    uri_queue_lock.acquire()
    uri_queue.append(uri)
    uri_queue_lock.release()

#####################################################################
#####################################################################
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
    
  startSender(30);
    
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
  
  
    
    
    
