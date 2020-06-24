# pylint: disable=C0103
# pylint: disable=C0301
# pylint: disable=C0326

"""
Decode wxflow messages into CHORDS compatible data structures.

The JSON configuration file must contain at least:
{
      "wxflow_decoders": [ ]
}

It is fine to include all of the configuration
needed by other modules (e.g. FromWxflow and ToChords).

The decoders list looks like:
[
  {
    "_enabled": true,
    "_wxflow_type": "ObsAir",
    "_chords_inst_id": "1",
    "_match": {
      "type": "obs_air",
      "serial_number": "AR-00005436"
    },
    "obs":[
        [0, "at"],
        [1, "pres"],
        [2, "tdry"],
        [3, "rh"],
        [4, "lcount"],
        [5, "ldist"],
        [6, "vbat"]
      ]
  },
  {
    "_enabled": true,
    "_wxflow_type": "HubStatus",
    "_chords_inst_id": "1",
    "_match": {
      "type": "hub_status",
      "serial_number": "HB-00004236"
    },
    "timestamp": {
      "chords_var": "at"
    },
    "rssi" :{
      "chords_var": "rssihub"
    }
  },
  {
    "_enabled": true,
    "_wxflow_type": "StationStatus",
    "_chords_inst_id": "1",
    "_match": {
      "type": "station_status",
      "serial_number": "AR-00005436"
    },
    "timestamp": {
      "chords_var": "at"
    },
    "voltage": {
        "chords_var": "vair"
    },
    "rssi": {
      "chords_var": "rssiair"
    },
    "sensor_status": {
      "chords_var": "statair"
    }
  }
]
"""


from json import loads
import sys

def msgMatch(wxflow_decoders, wxflow_msg):
    """See if the incoming message matches one of the match criteria.

    wxflow_decoders: a collection of wxflow message dictionaries,
    each containing at least a dictionary entry "_match",
    which contains key:value pairs for matching. If
    all of them exist in msg, then a message match will be validated.
    {
      "_match": {
        "type": "hub_status",
        "serial_number": "HB-00004236"
      }
    }

    Arguments:
    wxflow_deciders: -- A list of wxfow message decoders.
    wxflow_msg       -- a wxflow message object.

    Returns:
    If a match, return the decoder.
    Otherwise, return None.

    """
     # Iterate through the criteria, looking for a match
    for decoder in wxflow_decoders:
        if decoder['_enabled']:
            # Iterate through the match keys
            match_fields = decoder["_match"]
            for k in match_fields:
                # Does this key exist in the message?
                matched = True
                if k in wxflow_msg:
                    # Does the value match?
                    if wxflow_msg[k] != match_fields[k]:
                        matched = False
                        break

            if matched:
                return decoder

    return None

def extractChords(decoder, skey, wxflow_msg, test=False):
    """
    Apply the decoder to the wxflow message.

    It is assumed that the decoder matches the incoming message.

    Arguments:
    decoder    -- An entry from the
    wxflow_msg -- The wxflow message object

    Returns:
      {
        "inst_id": "id",
        "vars": {
          "var1_name": "var_value"},
           ...
          }
        "at": "timestamp (optional)"
      }
    """
    retval = [{}]

    # Create record 0
    i = 0
    if skey:
        retval[i]["skey"] = skey
    retval[i]["inst_id"] = decoder["_chords_inst_id"]
    retval[i]["test"] = test
    retval[i]["vars"] = {}

    # look through all of the decoder keys. If they don't begin with
    # an underscore, they are candidates for extraction from the
    # wxflow message. Add to record 0.
    for k in decoder:
        if k[0] != "_" and k != "obs":
            # "ob" is treated differently than all others
            if k != "obs":
                # Direct decode from a wxflow field.
                if k in wxflow_msg:
                    retval[0]["vars"][decoder[k]["chords_var"]] = wxflow_msg[k]

    # If no varibles were created, get rid of this record.
    if not retval[0]['vars']:
        retval = []

    # Now space through additional obs records, creating a new CHORDS record for each one.
    # (I wonder if weatherflow will ever deliver more than one? Seems like an
    # odd schema.)
    if 'obs' in decoder and 'obs' in wxflow_msg:
        for ob in wxflow_msg['obs']:
            retval.append({})
            i = len(retval) - 1
            if skey:
                retval[i]["skey"] = skey
            retval[i]["test"] = test
            retval[i]["inst_id"] = decoder["_chords_inst_id"]
            retval[i]["vars"] = {}
            for index, var_name in decoder['obs']:
                if index < len(ob):
                    retval[i]["vars"][var_name] = ob[index]

    return retval


def toChords(wxflow_config, wxflow_msg):
    """
    Use the config to convert a wxflow message to a CHORDS structure.

    Arguments:
    config -- the wxflow decoding configuration.
    msg    -- a wxflow message object.

    Returns:
    The CHORDS structure.
    """

    # Initialize return
    chords_values = None

    # Get the defined message types
    wxflow_decoders = wxflow_config["wxflow_decoders"]

    # Get the chords key
    if "skey" in wxflow_config:
        skey = wxflow_config["skey"]
    else:
        skey = None

    # Check for test
    if "test" in wxflow_config:
        test = wxflow_config["test"]
    else:
        test = False

    # Look for a match. A decoder is returned, if true.
    decoder = msgMatch(wxflow_decoders, wxflow_msg)

    # If we got a decoder, there is a message match.
    if decoder:
        # Break CHORDS stuff out of the message.
        chords_values = extractChords(decoder=decoder, skey=skey, test=test,
                                      wxflow_msg=wxflow_msg)

    return chords_values

#####################################################################
if __name__ == '__main__':

    sample_msgs = [
        '{"serial_number":"AR-00005436","type":"obs_air","hub_sn":"HB-00004236","obs":[[1511405107,772.40,9.05,63,0,0,3.47,1]],"firmware_revision":20}',
        '{"serial_number":"HB-00004236","type":"hub_status","firmware_version":"26","uptime":37587,"rssi":-59,"timestamp":1511405097,"reset_flags":503316482}',
        '{"serial_number":"AR-00005436","type":"station_status","hub_sn":"HB-00004236","timestamp":1511405107,"uptime":1774631,"voltage":3.47,"version":20,"rssi":-73,"sensor_status":0}',
        '{"serial_number":"AR-00005436","type":"obs_air","hub_sn":"HB-00004236","obs":[[1511405120,773.40,4.05,2,0,0,3.47,1],[1511405125,778.40,9.05,63,0,0,3.47,1]],"firmware_revision":20}'
        ]

    if len(sys.argv) != 2:
        print ("Usage:", sys.argv[0], "config_file")
        sys.exit(1)

    config = loads(open(sys.argv[1]).read())

    for jmsg in sample_msgs:
        # Convert json to an object
        wxflow = loads(jmsg)
        chords_stuff = toChords(config, wxflow)

        if chords_stuff:
            print(jmsg)
            for record in chords_stuff:
                print(record)
            print ("")
