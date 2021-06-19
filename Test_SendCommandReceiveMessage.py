from python_libratone_zipp.LibratoneZipp import LibratoneZipp
import socket
from python_libratone_zipp import LibratoneMessage

host = '192.168.1.31'

port_send = 7777
port_listen = 7778
# port_send = 3334
# port_listen = 3333

# SET = port=7777, command, data
# my_ba = LibratoneMessage.LibratoneMessage(command=15, data="20")
# GET = port=7777, command, data, commandType=1
my_ba = LibratoneMessage.LibratoneMessage(command=90, commandType=1)

my_ba.print_packet()

my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.bind(("", port_listen))
my_socket.sendto(my_ba.get_packet(), (host, port_send))

packet, ip = my_socket.recvfrom(1024)
message = LibratoneMessage.LibratoneMessage(packet=packet)

print(message.data)
print(message.data.decode())