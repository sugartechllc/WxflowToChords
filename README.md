# JSONtoCHORDS README

## About
JSONtoCHORDS is a python module for converting Weatherflow json formatted datagrams into the CHORDS
REST api, and submitting the data to a [CHORDS portal](http://chordsrt.com).

There are three python modules:
* FromWxflow: Capture datagrams and put them in a queue. This is multithreaded, so that datagram reading
  can occur in parallel with other processing.
* WxflowToChords: Translate the wxflow messages into structured data matching the CHORDS REST api. A 
  JSON based configuration specifies the translation.
* ToChords: Send the structured data to a CHORDS portal. This is multithreaded, so that http writing
  can occur in parallel with other processing. The same JSON configuration provides other information for
  the CHORDS connection.

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

## JSONtoCHORDS Configuration
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
