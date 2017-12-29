#! /usr/local/bin/python3
#
# # System modules
import json
import os
import time
import sys
from gc import collect

import FromWxflow
import DecodeWxflow
import ToChords

import pychords.tochords as tochords

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
    tochords.startSender()

    while True:

        collect()
        sys.stdout.flush()
        sys.stderr.flush() 
        time.sleep(1)
        wxflow_msgs = FromWxflow.get_msgs()
        for w in wxflow_msgs:
            wxflow_msg = json.loads(w)
            chords_records = DecodeWxflow.toChords(config, wxflow_msg)

            if chords_records:
                for chords_record in chords_records:
                    uri = tochords.buildURI(host, chords_record)
                    tochords.submitURI(uri, 720)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print ("Usage:", sys.argv[0], 'config_file')
        sys.exit (1)
        
    run(sys.argv[1])
