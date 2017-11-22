import json


if __name__ == '__main__':

    sample_msgs = [
        '{"serial_number":"HB-00004236","type":"hub_status","firmware_version":"25","uptime":35,"rssi":-63,"timestamp":0,"reset_flags":234881026}',
        '{"serial_number":"AR-00005436","type":"station_status","hub_sn":"HB-00004236","timestamp":0,"uptime":1729330,"voltage":3.43,"version":20,"rssi":-73,"sensor_status":4}',
        '{"serial_number":"AR-00005436","type":"obs_air","hub_sn":"HB-00004236","obs":[[1511359818,771.20,5.22,70,0,0,3.43,1]],"firmware_revision":20}'
        ]
    
    sample_config = """
    {
      "chords_host": "chords_host.com",
      "listen_port": 50222,
      "skey": "123456",
      "wxflow_msgs": {
        "AirObs": { 
          "_enabled": true,
          "_match": {
            "type": "obs_air",
            "serial_number": "AR-00005436"
          },
          "ob": {
            "chords_inst_id": "1", 
            "obs": [
              [0, "time"],
              [1, "pres"]
            ]
          }
        },
        "HubStatus": {
          "_enabled": true,
          "_match": {
            "type": "hub_status",
            "serial_number": "HB-00004236"
          },
          "rssi" :{
            "chords_inst_id": "1",
            "chords_var": "hubrssi"
          }
        },
        "AirStatus": {
          "_enabled": true,
          "_match": {
            "type": "station_status",
            "serial_number": "AR-00005436"
          },
          "voltage": {
              "chords_inst_id": "1",
              "chords_var": "airv"
          },
          "rssi": {
            "chords_inst_id": "1",
            "chords_var": "airrssi"
          },
          "sensor_status": {
            "chords_inst_id": "1",
            "chords_var": "airstat"
          }
        }
      }
    }
    """
    
    for msg in sample_msgs:
        wxflow_msg = json.loads(msg)
        print ("Sample Wxflow Message:")
        print(json.dumps(wxflow_msg, sort_keys=True, indent=2))
        
    print ("")
    print ("Sample Configuration:")
    config = json.loads(sample_config)
    print(json.dumps(config, sort_keys=True, indent=2))
    
        
