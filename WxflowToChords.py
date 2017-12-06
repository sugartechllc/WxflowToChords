try:
    import machine
    import WipyStat
    on_wipy = True
except:
    on_wipy = False
import json
import os
import time
import sys
from gc import collect

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
    ToChords.startSender()
    
    stat_count = 60
    while True:
        collect()
        time.sleep(1)
        wxflow_msgs = FromWxflow.get_msgs()
        for w in wxflow_msgs:
            wxflow_msg = json.loads(w)
            chords_records = DecodeWxflow.toChords(config, wxflow_msg)
            
            if chords_records:
                for chords_record in chords_records:
                    uri = ToChords.buildURI(host, chords_record)
                    ToChords.submitURI(uri, 60)
                    #mem_info()
        # Send Wipy status
        if on_wipy:
            stat_count = stat_count + 1
            if stat_count > 59:
                chords_record = WipyStat.toChords(config)
                uri = ToChords.buildURI(host, chords_record)
                ToChords.submitURI(uri, 60)
                stat_count = 0
    
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print ("Usage:", sys.argv[0], 'config_file')
        sys.exit (1)
        
    run(sys.argv[1])
