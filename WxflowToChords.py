#! /usr/local/bin/python3
"""
Full stack routing of wxflow datagrams to a CHORDS instance.

One configuration file provides all confguration for FromWxflow,
DecodeWxflow, and ToChords. See each module for a description
of the required configuration values.

"""

# pylint: disable=C0103
# pylint: disable=C0326
import json
import time
import sys

import FromWxflow
import DecodeWxflow
import pychords.tochords as tochords


def run(config_file):
    """
    Run the complete process.
    """
    print("Starting WxflowToChords with", config_file)
    config = json.loads(open(config_file).read())
    host   = config["chords_host"]
    port   = config["listen_port"]
    if "verbose" in config:
        verbose = config["verbose"]
    else:
        verbose = verbose = False

    FromWxflow.startReader(port)
    tochords.startSender()

    while True:
        sys.stdout.flush()
        sys.stderr.flush()
        time.sleep(1)
        wxflow_msgs = FromWxflow.get_msgs(verbose = verbose)
        for w in wxflow_msgs:
            wxflow_msg = json.loads(w)
            chords_records = DecodeWxflow.toChords(config, wxflow_msg)

            if chords_records:
                for chords_record in chords_records:
                    uri = tochords.buildURI(host, chords_record)
                    tochords.submitURI(uri, 10*60*24)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print ("Usage:", sys.argv[0], 'config_file')
        sys.exit (1)

    run(sys.argv[1])
