import json
import os
import time
import sys
import FromWxflow
import WxflowToChords

if len(sys.argv) != 2:
    print ("Usage:", sys.argv[0], 'config_file')
    sys.exit (1)
    
configfile = sys.argv[1]
config     = WxflowToChords.configload(sys.argv[1])

FromWxflow.start(port=50222)

while True:
    time.sleep(1)
    msgs = FromWxflow.get_msgs()
    for m in msgs:
        wxflow = json.loads(m)
        chords_stuff = WxflowToChords.toChords(config, wxflow)
        
        if chords_stuff:
            print (m)
            for record in chords_stuff:
                print (json.dumps(record, indent=2, sort_keys=True))
                       