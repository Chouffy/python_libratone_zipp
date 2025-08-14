import socket
import threading
from .LibratoneMessage import LibratoneMessage

# Zipp's UDP ports
_UDP_CONTROL_PORT = 7777          # where commands get sent
_UDP_RESULT_PORT = 7778           # where results arrive
_UDP_NOTIFICATION_RECV = 3333     # where notifications arrive
_UDP_NOTIFICATION_ACK  = 3334     # where ACKs for notifications get sent
_UDP_BUFFER_SIZE = 4096

class SocketHub:
    """
    Owns ONE notification socket (3333), ONE result socket (7778),
    and ONE shared sender socket. It demuxes incoming packets by source IP
    and forwards the raw bytes to the registered device's process_zipp_message.
    """
    def __init__(self):
        self._devices = {}   # ip -> device (must implement process_zipp_message(packet, port))
        self._running = True

        # Bind once: notifications and results
        self._notif_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._notif_sock.bind(("", _UDP_NOTIFICATION_RECV))

        self._result_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._result_sock.bind(("", _UDP_RESULT_PORT))

        # Unbound sender 
        self._send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Background threads for receiving
        self._t_notif = threading.Thread(
            target=self._rx_loop, args=(self._notif_sock, _UDP_NOTIFICATION_RECV, True),
            name="ZippHubNotif", daemon=True
        )
        self._t_result = threading.Thread(
            target=self._rx_loop, args=(self._result_sock, _UDP_RESULT_PORT, False),
            name="ZippHubResult", daemon=True
        )
        self._t_notif.start()
        self._t_result.start()

    # --- Public API ---------------------------------------------------------

    def register(self, device):
        """Call with a device that has `host` (IP string) and `process_zipp_message(bytes, port)`."""
        self._devices[device.host] = device

    def unregister(self, device):
        self._devices.pop(device.host, None)

    def send_control(self, host: str, packet: bytes):
        """Send a pre-built packet to the speaker's control port (7777)."""
        self._send_sock.sendto(packet, (host, _UDP_CONTROL_PORT))

    def stop(self):
        """Stop threads and sockets (optional clean shutdown)."""
        self._running = False
        try: 
            self._send_sock.sendto(b"", ("127.0.0.1", _UDP_NOTIFICATION_RECV))
        except: 
            pass
        try: 
            self._send_sock.sendto(b"", ("127.0.0.1", _UDP_RESULT_PORT))
        except: 
            pass
        for s in (self._notif_sock, self._result_sock, self._send_sock):
            try: 
                s.close()
            except: 
                pass

    # --- Internals ----------------------------------------------------------

    def _rx_loop(self, sock: socket.socket, rx_port: int, do_ack: bool):
        while self._running:
            try:
                data, (src_ip, _src_port) = sock.recvfrom(_UDP_BUFFER_SIZE)
            except OSError:
                break
            dev = self._devices.get(src_ip)
            if dev is not None:
                # Hand raw bytes to the device's existing parser
                dev.process_zipp_message(data, rx_port)

                # For notifications, send an ACK back (same format you already use)
                if do_ack:
                    ack = LibratoneMessage(command=0).get_packet()
                    self._send_sock.sendto(ack, (src_ip, _UDP_NOTIFICATION_ACK))
