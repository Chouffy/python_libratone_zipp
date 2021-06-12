import socket
import time
import binascii
import threading
import atexit

localIP = '192.168.1.10'
serverIP = '192.168.1.31'
receivePort = 3333
sendPort = 3334
sendTriggerPort = 7777
receiveResultPort = 7778
bufferSize  = 1024

# Ack packet: RemoteID = 0xaaaa, CommandType=2, no commands, no CRC, no payload
ba_ack = bytearray([0xaa, 0xaa, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
# Trigger packet: RemoteID = 0xaaaa, CommandType = 2, Command = 1284, CRC = 0xffff, no payload
ba_trigger = bytearray([0xaa, 0xaa, 0x02, 0x05, 0x04, 0x00, 0xff, 0xff, 0x00, 0x00])

ba_vol = bytearray([0xaa, 0xaa, 0x02, 0x05, 0x04, 0x00, 0xff, 0xff, 0x00, 0x00])

def process_incoming_zipp_message(message: bytearray):
    # remoteID = message[slice(0,1)]
    # commandType = message[2]
    command = message[3] << 8 | message[4]
    # commandStatus = message[5]
    # crc = message[slice(6,7)]
    # dataLen = message[slice(8,9)]
    data = message[slice(10,len(message))]
    
    try: print("command", command, "data", data.decode())
    except: print("command", command, "data", data)
    
# Create datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.bind((localIP, receivePort))
print("UDP server is up, listening on port", receivePort)

UDPServerSocket2 = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket2.bind((localIP, receiveResultPort))
print("UDP server is up, listening on port", receiveResultPort)

# Send trigger socket
UDPServerSocket.sendto(ba_trigger, (serverIP, sendTriggerPort))
print("Trigger packet sent")

# Listen for incoming data
while(True):
    # Wait for new packet; address is the originating IP:port
    message, address = UDPServerSocket.recvfrom(bufferSize)

    thread = threading.Thread(target=process_incoming_zipp_message, args=(message,))
    thread.start()

    # Send the ack
    UDPServerSocket.sendto(ba_ack, (serverIP, sendPort))
