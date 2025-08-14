import socket
import threading
from .LibratoneMessage import LibratoneMessage

# Zipp's UDP ports
_UDP_CONTROL_PORT = 7777          # where commands get sent
_UDP_RESULT_PORT = 7778           # where results arrive
_UDP_NOTIFICATION_RECV = 3333     # where notifications arrive
_UDP_NOTIFICATION_ACK  = 3334     # where ACKs for notifications get sent
_UDP_BUFFER_SIZE = 4096

