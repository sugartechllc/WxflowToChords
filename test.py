import socket
import json

UDP_PORT = 50222

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind(('', UDP_PORT))

while True:
    jbytes, addr = sock.recvfrom(2000) 
    msg = json.loads(jbytes.decode('utf-8'))
    print(json.dumps(msg, indent=4))
