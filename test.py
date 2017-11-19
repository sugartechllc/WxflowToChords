import socket

import socket
UDP_PORT = 50222
 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('',50222))

while True:
    data, addr = sock.recvfrom(2000) 
    print addr, data