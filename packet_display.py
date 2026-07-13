# Snoop on port 50222 
#
# To get pretty-printed JSON, pipe into jq:
# python packet_display.py | jq .
#
# To get pretty-printed JSON of a particular packet, 
# select it:
# python packet_display.py | jq 'select(.type=="obs_st")'

python3 -u -c "
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('0.0.0.0', 50222))
while True:
    data, addr = s.recvfrom(4096)
    print(data.decode())
"
