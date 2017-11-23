import json
import sys

#####################################################################
def configloads(config_string):
    """
    Read the json configuration from a string.
    Return the decoded object.
    """
    config = json.loads(config_string)
    return config

#####################################################################
def configload(config_file):
    """
    Read the json configuration from a file.
    Return the decoded object.
    """
    config = configloads(open(config_file).read())
    return config

#####################################################################
def msgMatch(wxflow_decoders, wxflow_msg):
    """
    See if the incoming message matches one of the match criteria.
    If so, return the match criteria. 
    Otherwise, return None.
    
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
    
    wxflow_msg: a wxflow message object.
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
    
#####################################################################
def extractChords(decoder, skey, wxflow_msg):
    """
    Apply the decoder to the wxflow message. It
    is assumed that the decoder matches the incoming message.
    
    decoder: An entry from the 
    wxflow_msg: The wxflow message object
    
    Return: 
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
    if len(retval[0]['vars']) == 0:
        retval = []
    
    # Now space through the obs records, creating a new CHORDS record for each one.
    # (I wonder if weatherflow will ever deliver more than one? Seems like an
    # odd schema.)
    if 'obs' in decoder and 'obs' in wxflow_msg:
        for ob in wxflow_msg['obs']:
            retval.append({})
            i = len(retval) - 1
            if skey:
                retval[i]["skey"] = skey 
            retval[i]["inst_id"] = decoder["_chords_inst_id"]
            retval[i]["vars"] = {}
            for index,var_name in decoder['obs']:
                if index < len(ob):
                    retval[i]["vars"][var_name] = ob[index]

    return retval
    
#####################################################################
def toChords(config, wxflow_msg):
    """
    config: the wxflow decoding configuration.
    msg:    a wxflow message object.
    """
    
    # Initialize return
    chords_stuff = None
    
    # Get the defined message types
    wxflow_decoders = config["wxflow_decoders"]
    
    # Get the chords key
    if "skey" in config:
        skey = config["skey"]
    else:
        skey = None
    
    # Look for a match. A decoder is returned, if true.
    decoder = msgMatch(wxflow_decoders, wxflow_msg)
    
    # If we got a decoder, there is a message match.
    if decoder:
        # Break CHORDS stuff out of the message.
        chords_stuff = extractChords(decoder, skey, wxflow_msg)
        
    return chords_stuff

#####################################################################
#####################################################################
if __name__ == '__main__':

    sample_msgs = [
        '{"serial_number":"AR-00005436","type":"obs_air","hub_sn":"HB-00004236","obs":[[1511405107,772.40,9.05,63,0,0,3.47,1]],"firmware_revision":20}',
        '{"serial_number":"HB-00004236","type":"hub_status","firmware_version":"26","uptime":37587,"rssi":-59,"timestamp":1511405097,"reset_flags":503316482}',
        '{"serial_number":"AR-00005436","type":"station_status","hub_sn":"HB-00004236","timestamp":1511405107,"uptime":1774631,"voltage":3.47,"version":20,"rssi":-73,"sensor_status":0}',
        '{"serial_number":"AR-00005436","type":"obs_air","hub_sn":"HB-00004236","obs":[[1511405120,773.40,4.05,2,0,0,3.47,1],[1511405125,778.40,9.05,63,0,0,3.47,1]],"firmware_revision":20}'
        ]
    
    sample_config = """
    {
      "chords_host": "chords_host.com",
      "listen_port": 50222,
      "skey": "123456",
      "wxflow_decoders": [
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
    }
    """

    if (len(sys.argv) == 1):
        config = configloads(sample_config)
    else:
        config = configload(sys.argv[1])
     
    for jmsg in sample_msgs:
        # Convert json to an object
        wxflow = json.loads(jmsg)
        chords_stuff = toChords(config, wxflow)
        
        if chords_stuff:
            print (jmsg)
            for record in chords_stuff:
                print (record)
            print ("")
