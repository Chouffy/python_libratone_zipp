from python_libratone_zipp.LibratoneZipp import LibratoneZipp
import socket, threading
from python_libratone_zipp import LibratoneZipp, LibratoneMessage

host = '192.168.1.31'

_PRINT_EACH_BYTE = False

_UDP_BUFFER_SIZE = 4096
_UDP_CONTROL_PORT = 7777                 # Port to send a command
_UDP_RESULT_PORT = 7778                  # Port to receive the result of a command??
_UDP_NOTIFICATION_SEND_PORT = 3334       # Port to send ack to the speaker after a notification
_UDP_NOTIFICATION_RECEIVE_PORT = 3333    # Port to receive notification from the speaker

# Setup 2 thread to monitor incoming messages - sometime the first message is empty

def process_zipp_message(packet: bytearray, receive_port):
    zipp_message = LibratoneMessage.LibratoneMessage(packet=packet)
    command = zipp_message.get_command_int()
    data = zipp_message.data
    try: pretty_data = data.decode()
    except: pretty_data = data
    print("COMMAND:", command, "DATA:", pretty_data, "PORT:", receive_port)

    if _PRINT_EACH_BYTE:
        i = 0
        for item in data:
            print(data[i])
            i+=1

def listen_incoming_zipp_notification(socket, receive_port, ack_port=None):
    while True:
        message, address = socket.recvfrom(_UDP_BUFFER_SIZE)
        thread = threading.Thread(target=process_zipp_message, name="Process_Zipp_Message", args=[message, receive_port])
        thread.start()
        # Send the ack
        if ack_port != None: socket.sendto(LibratoneMessage.LibratoneMessage(command=0).get_packet(), (host, _UDP_NOTIFICATION_SEND_PORT))
def thread_setup():
    # Thread for _UDP_RESULT_PORT
    my_socket_UDP_RESULT_PORT = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket_UDP_RESULT_PORT.bind(("", _UDP_RESULT_PORT))
    thread_UDP_RESULT_PORT = threading.Thread(target=listen_incoming_zipp_notification,  name="Listen_incoming_"+str(_UDP_RESULT_PORT), args=[my_socket_UDP_RESULT_PORT, _UDP_RESULT_PORT, _UDP_CONTROL_PORT])
    thread_UDP_RESULT_PORT.start()

    # Thread for _UDP_NOTIFICATION_RECEIVE_PORT
    my_socket_UDP_NOTIFICATION_RECEIVE_PORT = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket_UDP_NOTIFICATION_RECEIVE_PORT.bind(("", _UDP_NOTIFICATION_RECEIVE_PORT))
    thread_UDP_NOTIFICATION_RECEIVE_PORT = threading.Thread(target=listen_incoming_zipp_notification,  name="Listen_incoming_"+str(_UDP_RESULT_PORT), args=[my_socket_UDP_NOTIFICATION_RECEIVE_PORT, _UDP_NOTIFICATION_RECEIVE_PORT, _UDP_NOTIFICATION_SEND_PORT])
    thread_UDP_NOTIFICATION_RECEIVE_PORT.start()

thread_setup()

# SET = port=7777, command, data
# my_ba = LibratoneMessage.LibratoneMessage(command=15, data="20")
# GET = port=7777, command, data, commandType=1
my_ba = LibratoneMessage.LibratoneMessage(command=515, commandType=1)

# my_ba.print_packet()

my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
port_send = _UDP_CONTROL_PORT
while True:
    print("Command will be send on", port_send, "\n")
    my_socket.sendto(my_ba.get_packet(), (host, port_send))
    input("Press enter to resend\n")
