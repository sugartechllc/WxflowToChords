# JSONtoCHORDS README

## About
JSONtoCHORDS is a python module for converting json formatted datagrams into the CHORDS
REST api, and submitting the data to a [CHORDS portal](http://chordsrt.com).

## JSON Input Schema
Input data is structured according to the Weatherflow 
[UDP api](https://weatherflow.github.io/SmartWeather/api/udp.html).
Messages have  a`type` field identifying the type of message,
status fields indicating hardware health, 
and in some cases an `ob` array containing the weather values in a specific order. 

Unfortunately, the meaning of each `ob` array element is not identified in the message; you
have to refer to the documentation to determine this. Other values, such as voltage and rssi,
can be located by identifier.

For example:

```
{
  "serial_number": "SK-00008453",
  "type":"rapid_wind",
  "device_id":1110,
  "hub_sn": "HB-00000001",
  "ob":[1493322445,2.3,128]
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

## Configuration
A JSON structure defines the mapping between the input data and the CHORDS portal api.

```
"chords_host": "chords_host.com",

"listen_port": 50222,

"skey": "123456",

"msg_types" : {
  "rapid_wind":
    [
         {
           "pos:" : 0,
           "chords_short_name" : "time"
         },
         {
           "pos:" : 1,
           "chords_short_name" : "wspd"
         },
         {
           "pos:" : 2,
           "chords_short_name" : "wdir"
  ]
}

"messages": {
  "SugarTechLLC": { 
    "enabled": true,
    "weatherflow": {
      "msg_type": "rapid_wind"
      "serial_number": "SK-00008453",
      "device_id":1110,
      "hub_sn": "HB-00000001"
    },
    "chords" : {
      "chords_inst_id": 1
    }
  },
  "SwellCentral": {
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
```
