# UDPtoCHORDS README

## About
UDPtoCHORDS is a python module for converting json formatted datagrams into the CHORDS Rest api, 
and submitting the data to a CHORDS portal.

## Configuration
JSON

## Micropython on OSX
```
brew install libffi
git clone --recurse https://github.com/micropython/micropython.git
cd micropython/ports/unix
make axtls
PKG_CONFIG_PATH=/usr/local/opt/libffi/lib/pkgconfig make install
./micropython
```
