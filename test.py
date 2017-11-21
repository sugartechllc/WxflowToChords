import json
import os
import time
import wxflow

wxflow.start(port=50222)

while True:
    time.sleep(1)
    msgs = wxflow.get_msgs()
    for o in msgs:
        print (o.decode('UTF-8'))
    

