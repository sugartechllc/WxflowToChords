import json
import os
import time
import FromWxflow

FromWxflow.start(port=50222)

while True:
    time.sleep(1)
    msgs = FromWxflow.get_msgs()
    for o in msgs:
        print (o.decode('UTF-8'))
    

