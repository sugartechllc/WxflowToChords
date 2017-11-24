# WxflowToChords README

## About
WxflowToChords are a set of python modules for converting Weatherflow json formatted datagrams into the CHORDS
REST api, and submitting the data to a [CHORDS portal](http://chordsrt.com).

There are four python modules:
* FromWxflow: Capture datagrams and put them in a queue. This is multithreaded, so that datagram reading
  can occur in parallel with other processing.
* DecodeWxflow: Translate the wxflow messages into structured data matching the CHORDS REST api. A 
  JSON based configuration specifies the translation.
* ToChords: Send the structured data to a CHORDS portal. This is multithreaded, so that http writing
  can occur in parallel with other processing. The same JSON configuration provides other information for
  the CHORDS connection.
* WxflowToChords: Strings all three modules together for the end-to-end process.

Each module expects a configuration, provided in a JSON file. A single file can contain the
configuration for all modules, or a file can be created for just the items needed for a gven module.

Each module will run a test case if it is invoked individually.

This code will be run on both regular computers, and micropython systems such as the WiPy. Thus
the code must be python3 compatible, as well as micropython compatible. The [Unix version of
micropython](https://github.com/micropython/micropython/wiki/Getting-Started) can be used to 
verify comaptibility for the latter.

## Weatherflow JSON Schema
Input data is structured according to the Weatherflow 
[UDP JSON schema](https://weatherflow.github.io/SmartWeather/api/udp.html).
Messages have  a`type` field identifying the type of message,
status fields indicating identity and hardware health, 
and in some cases an `obs` array containing the observed values, in a predefined order. 

Unfortunately, the meaning of each `obs` array element is not identified in the message; you
have to refer to the documentation to determine this. Other values, such as voltage and rssi,
can be located by identifier.

For example:

```
{
  "serial_number":"HB-00000001",
  "type":"hub_status",
  "firmware_revision":"13",
  "uptime":1670133,
  "rssi":-62,
  "timestamp":1495724691,
  "reset_flags": 234881026,
  "stack": "1616,1608"
}
```
```
{
  "serial_number": "SK-00008453",
  "type":"rapid_wind",
  "device_id":1110,
  "hub_sn": "HB-00000001",
  "obs":[1493322445,2.3,128]
}
```
```
{
  "serial_number": "AR-00004049",
  "type": "device_status",
  "hub_sn": "HB-00000001",
  "timestamp": 1510855923,
  "uptime": 2189,
  "voltage": 3.50,
  "firmware_revision": 17,
  "rssi": -17,
  "sensor_status": 0
}
```
The WeatherFlow documentation seems to be in flux, so be sure to capture some datagrams
to verify what they are transmitting.

## DecodeWxflow Configuration
A JSON structure defines the mapping between the wxflow input data and the CHORDS portal api.
A collection of wxflow messages are defined (`wxflow_msgs`). Each one contains a list of 
match attributes. If an incoming messages matches one of the `wxflow_msgs`, that entry is 
used to decode the message.

The `wxflow_type` in `wxflow_decoders` (e.g. "ObsAir") are user-assigned, and have no special meaning.

Within each message decoding specification, there are two types of keys. If one
begins with an underscore, it is a directive to the decoder, such as `_enabled` or
`_match`. Otherwise, it is a key that will match a field in the incoming message,
and the element directs further message handling.

The `obs` element has special meaning. It contains instructions on how to
route the elements of an wxflow `obs` array.

If a CHORDS variable is identified as `at`, it will be converted to a timestamp and used for
the `at=` timestamp.
```
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
```

## WxToChords

Typical decoding; with the wxflow message followed by the CHORDS structured data:
```
{"serial_number":"HB-00004236","type":"hub_status","firmware_version":"26","uptime":88638,"rssi":-58,"timestamp":1511456148,"reset_flags":503316482}
{
  "inst_id": "1",
  "skey": "123456",
  "vars": {
    "at": 1511456148,
    "rssihub": -58
  }
}
{"serial_number":"AR-00005436","type":"station_status","hub_sn":"HB-00004236","timestamp":1511456154,"uptime":1825691,"voltage":3.46,"version":20,"rssi":-73,"sensor_status":4}
{
  "inst_id": "1",
  "skey": "123456",
  "vars": {
    "at": 1511456154,
    "rssiair": -73,
    "statair": 4,
    "vair": 3.46
  }
}
{"serial_number":"AR-00005436","type":"obs_air","hub_sn":"HB-00004236","obs":[[1511456154,770.00,13.43,33,0,0,3.46,1]],"firmware_revision":20}
{
  "inst_id": "1",
  "skey": "123456",
  "vars": {
    "at": 1511456154,
    "lcount": 0,
    "ldist": 0,
    "pres": 770.0,
    "rh": 33,
    "tdry": 13.43,
    "vbat": 3.46
  }
}
```

## Micropython on OSX
```
brew install libffi
git clone --recurse https://github.com/micropython/micropython.git
cd micropython/ports/unix
make axtls
PKG_CONFIG_PATH=/usr/local/opt/libffi/lib/pkgconfig make install
./micropython
>>> import upip
>>> upip.install('micropython-socket')
>>> upip.install('micropython-json')
>>> upip.install('micropython-thread')
>>> upip.install('micropython-os')
```
