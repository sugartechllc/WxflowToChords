import socket
import _thread
import time

wxflow_msg_queue = []
wxflow_msg_queue_lock = _thread.allocate_lock()

def msg_capture(port):
    global wxflow_msg_queue
    global wxflow_msg_queue_lock
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', port))
    while True:
        jbytes, addr = sock.recvfrom(2000)
        #print (jbytes.decode('utf-8'))
        wxflow_msg_queue_lock.acquire()
        wxflow_msg_queue.append(jbytes)
        wxflow_msg_queue_lock.release()
    
def get_msgs():
    '''
    Return a list containing new messages. If none are 
    available, the list is empty.
    '''
    global wxflow_msg_queue
    global wxflow_msg_queue_lock
    
    msg_list = []
    wxflow_msg_queue_lock.acquire()
    for m in wxflow_msg_queue:
        msg_list.append(wxflow_msg_queue.pop(0))
    wxflow_msg_queue_lock.release()
    return msg_list

def start(port):
    _thread.start_new_thread(msg_capture, (port,))
