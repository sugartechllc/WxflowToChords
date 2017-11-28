import json
import os
import time
import sys

import FromWxflow
import DecodeWxflow
import ToChords

"""
Full stack routing of wxflow datagrams to a CHORDS instance.

One configuration file provides all confguration for FromWxflow,
DecodeWxflow, and ToChords. See each module for a description
of the required configuration values.

"""
def run(config_file):
    print("Starting WxflowToChords with", config_file)
    config = json.loads(open(config_file).read())
    host   = config["chords_host"]
    port   = config["listen_port"]
    
    FromWxflow.startReader(port)
    
    ToChords.startSender(10)
    
    while True:
        time.sleep(1)
        wxflow_msgs = FromWxflow.get_msgs()
        for w in wxflow_msgs:
            wxflow_msg = json.loads(w)
            chords_stuff = DecodeWxflow.toChords(config, wxflow_msg)
            
            if chords_stuff:
                print (wxflow_msg)
                for chords_record in chords_stuff:
                    print (json.dumps(chords_record))
                    uri = ToChords.buildURI(host, chords_record)
                    print (uri)
                    ToChords.submitURI(uri)
    
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print ("Usage:", sys.argv[0], 'config_file')
        sys.exit (1)
        
    run(sys.argv[1])
