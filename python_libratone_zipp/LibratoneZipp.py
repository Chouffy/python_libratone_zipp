#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Automation Library for Libratone speakers like Libratone Zipp.
License: see LICENSE file
"""

import logging
import socket
import threading
from . import LibratoneMessage

_DEBUG = False # Activate some verbose print()
_LOGGER = logging.getLogger("LibratoneZipp")

# Define state variables
STATE_OFF = "OFF"
STATE_SLEEP = "SLEEP"
STATE_IDLE = "IDLE"
STATE_PLAY = "PLAY"
STATE_PAUSE = "PAUSE"
STATE_STOP = "STOP"

# Define network variables
_UDP_CONTROL_PORT = 7777                 # Port to send a command
_UDP_RESULT_PORT = 7778                  # Port to receive the result of a command
_UDP_NOTIFICATION_RECEIVE_PORT = 3333    # Port to receive notification from the speaker
_UDP_NOTIFICATION_SEND_PORT = 3334       # Port to send ack (?) to the speaker after a notification
_UDP_BUFFER_SIZE = 1024

# Define Zipp commands ID
_COMMAND_TABLE = {
    'Version': {
        # from com.libratone.model.LSSDPNode, fetchVersion
        '_command': 5,
    },
    'PlayControl': {
        # from com.libratone.model.LSSDPNode, setPlayControl
        '_command': 40,
        # from com.libratone.luci.PlayControlCommand
        'play': 'PLAY',
        'stop': 'STOP',
        'pause': 'PAUSE',
        'next': 'NEXT',
        'prev': 'PREV',
    },
    'PlayStatus': {
        # from com.libratone.model.LSSDPNode, fetchPlayStatus
        '_command': 51,
        # from com.libratone.luci.PlayControlCommand - more state are defined
        'play': b'0',
        'stop': b'1',
        'pause': b'2',
    },
    'Volume': {
        # from com.libratone.model.LSSDPNode, fetchVolume and setVolume
        '_command': 64,
    },
    'DeviceName': {
        # from com.libratone.model.LSSDPNode, fetchDeviceName
        '_command': 90,
    },
    'Player': {
        # from com.libratone.model.LSSDPNode, setPlayer
        '_command': 277,
        # Favorites, captured:
        'favorite': {
            '1': '{"isFromChannel":false,"play_identity":"1","play_subtitle":"1","play_title":"channel","play_type":"channel","token":""}',
            '2': '{"isFromChannel":false,"play_identity":"2","play_subtitle":"2","play_title":"channel","play_type":"channel","token":""}',
            '3': '{"isFromChannel":false,"play_identity":"2","play_subtitle":"3","play_title":"channel","play_type":"channel","token":""}',
            '4': '{"isFromChannel":false,"play_identity":"2","play_subtitle":"4","play_title":"channel","play_type":"channel","token":""}',
            '5': '{"isFromChannel":false,"play_identity":"2","play_subtitle":"5","play_title":"channel","play_type":"channel","token":""}',
        },
    },
    'Voicing': {
        # from com.libratone.model.LSSDPNode, setVoicing
        '_command': 518,
        # from com.libratone.enums.Voicing - more voicings are defined (extra bass, enhanced treble, smart) but those aren't accessible to the Libratone Zipp 1
        'neutral': {
            '_data': 'V100',
            'name': 'Neutral',
            'description': 'Basic neutral setting',
        }, 'easy': {
            '_data': 'V101',
            'name': 'Easy Listening',
            'description': 'Easy and smooth leaned back sound',
        }, 'soft': {
            '_data': 'V102',
            'name': 'Soft & Comfortable',
            'description': 'Soft midrange for compressed recordings',
        }, 'rock': {
            '_data': 'V103',
            'name': 'Rock The House',
            'description': 'Extra drum kick - smooth midrange',
        }, 'jazz': {
            '_data': 'V104',
            'name': 'Jazz Club',
            'description': 'Open acoustic sound, focus on voices',
        }, 'movie': {
            '_data': 'V105',
            'name': 'Movie Mode',
            'description': 'Extra action and movie re-equalization',
        }, 'live': {
            '_data': 'V106',
            'name': 'Live Concert',
            'description': 'Where the music is loud and dynamic',
        }, 'classical': {
            '_data': 'V107',
            'name': 'Classical',
            'description': 'Enjoy grand pianos when they are best',
        }, 'speech': {
            '_data': 'V108',
            'name': 'Speech',
            'description': 'For TV programs with subtle voices',
        }, 
    },
    'ChargingStatus': {
        # from com.libratone.model.LSSDPNode, fetchChargingStatus
        # Used for trigger
        '_command': 1284,
    },
}

class LibratoneZipp:
    """Representing a Libratone Zipp device."""

    def __init__(self, host, name="Zipp"):
        # Configuration
        self._localHost = socket.gethostbyname(socket.gethostname())
        self._host = host
        self._name = name
        
        # Active variables
        self._state = None
        self._voicing = None
        self._volume = None

        # Variables fixed for the lifecycle
        self._voicing_list = None
        
        # Network
        self._listening_notification_flag = True   # Flag to shut down the thread
        self._listening_notification_socket, self._listening_notification_thread = self._get_new_socket(_UDP_NOTIFICATION_RECEIVE_PORT, _UDP_CONTROL_PORT)

        self._listening_result_flag = True
        # self._listening_result_socket, self._listening_result_thread = self._get_new_socket(_UDP_RESULT_PORT)

    def exit(self):
        self._listening_notification_flag = False
        self._listening_result_flag = False
        print("Disconnected from Libratone Zipp, waiting for last packet.")

    @property
    def name(self): return self._name
    @property
    def host(self): return self._host
    @property
    def state(self): return self._state
    @property
    def voicing(self): return self._voicing
    @property
    def volume(self): return self._volume
    
    # TODO Rework
    @property
    def voicing_list(self):
        list = []
        for voicing_id in VOICING:
            list.append(voicing_id)
        return list

    # Interpret message from Zipp
    def process_zipp_message(self, message: bytearray):
        
        zipp_message = LibratoneMessage.LibratoneMessage()
        zipp_message.set_from_packet(message)

        command = zipp_message.command
        data = zipp_message.data
        
        if _DEBUG: print("\nCOMMAND:", command, "DATA:", data)

        if command == 0: print("placeholder to start at 0")
        elif command == _COMMAND_TABLE['PlayStatus']['_command'] and data == _COMMAND_TABLE['PlayStatus']['play']: self._state = STATE_PLAY
        elif command == _COMMAND_TABLE['PlayStatus']['_command'] and data == _COMMAND_TABLE['PlayStatus']['stop']: self._state = STATE_STOP
        elif command == _COMMAND_TABLE['PlayStatus']['_command'] and data == _COMMAND_TABLE['PlayStatus']['pause']: self._state = STATE_PAUSE
        elif command == _COMMAND_TABLE['Volume']['_command']: self._volume = data.decode()
        elif command == _COMMAND_TABLE['Voicing']['_command']: self._voicing = data.decode()
        else:
            try: pretty_data = data.decode()
            except: pretty_data = data
            finally: print("\nCOMMAND:", command, "DATA:", pretty_data)

    # Wait for a message from the Zipp and start a thread to process it
    def listen_incoming_zipp_notification(self, socket):
        print("Listening incoming Zipp messages")
        while(self._listening_notification_flag):
            # Wait for new packet; address is the originating IP:port
            message, address = socket.recvfrom(_UDP_BUFFER_SIZE)
            thread = threading.Thread(target=self.process_zipp_message, args=[message])
            thread.start()

            # Send the ack
            socket.sendto(LibratoneMessage.LibratoneMessage(0).get_packet(), (self._host, _UDP_NOTIFICATION_SEND_PORT))

    def _get_new_socket(self, receive_port, send_port=""):
        try:
            _new_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

            # Instanciate a thread to manage incoming messages
            _new_thread = threading.Thread(target=self.listen_incoming_zipp_notification, args=[_new_socket])
            _new_thread.start()

            # Set up a listening socker
            _new_socket.bind((self._localHost, receive_port))

            if send_port !="":
                # Send trigger and instanciate a thread to manage incoming messages
                _new_socket.sendto(LibratoneMessage.LibratoneMessage(_COMMAND_TABLE['ChargingStatus']['_command']).get_packet(), (self._host, send_port))

            # TODO Maybe a keep-alive thread (send ba_ack every 10 min) will be needed
            return _new_socket, _new_thread

        except ConnectionError as connection_error:
            _LOGGER.warning("Connection error: %s", connection_error)
            self._state = STATE_OFF
            return None
        except socket.gaierror as socket_gaierror:
            _LOGGER.warning("Address-related error: %s", socket_gaierror)
            self._state = STATE_OFF
            return None
        except socket.error as socket_error:
            _LOGGER.warning("Socket error: %s", socket_error)
            self._state = STATE_OFF
            return None

    def send_command(self, zipp_command, zipp_data=""):
        if self._listening_notification_socket is None:
            self._listening_notification_socket = self._get_new_socket()

        try:
            # Generate the message
            message = LibratoneMessage.LibratoneMessage(zipp_command, zipp_data).get_packet()

            # Send a store the answer in resp
            resp = self._listening_notification_socket.sendto(message, (self._host, _UDP_CONTROL_PORT))

            if resp == 0:
                self._listening_notification_socket.close()
                self._listening_notification_socket = None
                self._state = STATE_OFF
                _LOGGER.warning("Send fail, disconnecting from Libratone Zipp")

        except (BrokenPipeError, ConnectionError) as connect_error:
            _LOGGER.warning("Connection error, retrying. %s", connect_error)
            self._listening_notification_socket = None
            self._listening_notification_socket = self._get_new_socket(self._host, _UDP_CONTROL_PORT)
            if self._listening_notification_socket is not None:
                # retrying after broken pipe error
                self._listening_notification_socket.sendto(command.encode(), (self._host, _UDP_CONTROL_PORT))
    
    def _playcontrol(self, action):
        # Possible actions are defined in _COMMAND_TABLE['PlayControl']
        try:
            self.send_command(_COMMAND_TABLE['PlayControl']['_command'], _COMMAND_TABLE['PlayControl'][action])
            return True
        except:
            _LOGGER.warning("Error: " + action + " command not sent.")
            return False

    def play(self): return self._playcontrol('play')
    def pause(self): return self._playcontrol('pause')
    def stop(self): return self._playcontrol('stop')
    def next(self): return self._playcontrol('next')
    def prev(self): return self._playcontrol('prev')

    def favorite_play(self, favourite_id):
        if int(favourite_id) < 1 or int(favourite_id) > 5:
            _LOGGER.warning("Error: favorite command must be within 1 and 5.")
            return False
        try:
            # if favourite_id is a string
            if isinstance(favourite_id, str): self.send_command(_COMMAND_TABLE['Player']['_command'], _COMMAND_TABLE['Player']['favorite'][favourite_id])
            else: self.send_command(_COMMAND_TABLE['Player']['_command'], _COMMAND_TABLE['Player']['favorite'][str(favourite_id)])
            return True
        except:
            _LOGGER.warning("Error: favorite command not sent.")
            return False

    def voicing_set(self, voicing_id):
        try:
            self.send_command(_COMMAND_TABLE['Voicing']['_command'], _COMMAND_TABLE['Voicing'][voicing_id]['_data'])
            return True
        except:
            _LOGGER.warning("Error: voicing command not sent.")
            return False

    def volume_set(self, volume):
        if int(volume) < 0 or int(volume) > 100:
            _LOGGER.warning("Error: volume command must be within 0 and 100.")
            return False
        try:
            # if volume is a string
            if isinstance(volume, str): self.send_command(_COMMAND_TABLE['Volume']['_command'], volume)
            else: self.send_command(_COMMAND_TABLE['Volume']['_command'], str(volume))
            return True
        except:
            _LOGGER.warning("Error: volume command not sent.")
            return False

    