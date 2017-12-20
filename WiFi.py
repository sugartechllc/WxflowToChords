import os
import platform

airport_cmd = \
    "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I"

test_output = """
    agrCtlRSSI: -73
    agrExtRSSI: 0
    agrCtlNoise: -93
    agrExtNoise: 0
    state: running
    op mode: station 
    lastTxRate: 81
    maxRate: 300
    lastAssocStatus: 0
    802.11 auth: open
    link auth: wpa2-psk
    BSSID: e0:91:f5:2:5f:eb
    SSID: ssid_name
    MCS: 4
    channel: 153,-1
"""

def os_type():
    """
    """
    p = platform.platform()
    if 'Darwin' in p:
        return 'darwin'
    if 'debian' in p:
        return 'debian'

def darwin_wifi():
    """

    agrCtlRSSI: -73
    agrExtRSSI: 0
    agrCtlNoise: -93
    agrExtNoise: 0
    state: running
    op mode: station 
    lastTxRate: 81
    maxRate: 300
    lastAssocStatus: 0
    802.11 auth: open
    link auth: wpa2-psk
    BSSID: e0:91:f5:2:5f:eb
    SSID: your_ssid
    MCS: 4
    channel: 153,-1
    """

    p = os.popen(airport_cmd, 'r')
    cmd_out = p.read()
    lines = cmd_out.split("\n")
    retval = {}
    for l in lines:
        ll = l.strip()
        pair = ll.split(": ")
        pair[0] = pair[0].replace(" ", "_")
        if len(pair) == 2:
            retval[pair[0]] = pair[1]
    return retval

def wifi():
    os = os_type()
    if os == 'darwin':
        return darwin_wifi()

    return {}

def main():
    wifi_info = wifi()
    for key in ('SSID', 'agrCtlRSSI'):
        if key in wifi_info:
            print(key + ":", wifi_info[key])

if __name__ == '__main__':
    main()


