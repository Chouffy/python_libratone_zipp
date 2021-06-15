#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Control Library for Libratone speakers like Libratone Zipp.
License: see LICENSE file
"""

import logging
import time
import socket
import threading
from . import LibratoneMessage

_LOGGER = logging.getLogger("LibratoneZipp")
_LOG_UNKNOWN_PACKET = False                     # Print unknown packet

# Define fixed variables
STATE_OFF = "OFF"
STATE_PLAY = "PLAY"
STATE_PAUSE = "PAUSE"
STATE_STOP = "STOP"

# Define network variables
_UDP_CONTROL_PORT = 7777                 # Port to send a command
_UDP_RESULT_PORT = 7778                  # Port to receive the result of a command??
_UDP_NOTIFICATION_SEND_PORT = 3334       # Port to send ack to the speaker after a notification
_UDP_NOTIFICATION_RECEIVE_PORT = 3333    # Port to receive notification from the speaker

_UDP_BUFFER_SIZE = 1024
_KEEPALIVE_CHECK_PERIOD = 30            # Time in second between each keep-alive check 

# Define Zipp commands ID
_COMMAND_TABLE = {
    # com.libratone.model.LSSDPNode , fetchAllForWifi contain all useful fonctions 
    'Version': {
        '_get': 5,      # from com.libratone.model.LSSDPNode, fetchVersion
    },
    'CurrPowerMode': {
        '_get': 14,     # from com.libratone.model.LSSDPNode, fetchCurrPowerMode - but no reply when asked?
    },
    'PowerMode': {
        # Used for sleep timer
        '_set': 15,     # from com.libratone.model.LSSDPNode, setPowerMode        
        '_get': 15,     # from com.libratone.model.LSSDPNode, setOffTime - format for timer data is "2" + j, j being ??      
        'sleep': 20,    # from com.libratone.model.LSSDPNode, triggerDeviceSleep 
        'wakeup': 00,   # from com.libratone.model.LSSDPNode, triggerDeviceWakeup
    },
    'PlayControl': {
        '_set': 40,     # # from com.libratone.model.LSSDPNode, setPlayControl
        # from com.libratone.luci.PlayControlCommand
        'play': 'PLAY',
        'stop': 'STOP',
        'pause': 'PAUSE',
        'next': 'NEXT',
        'prev': 'PREV',
    },
    'PlayStatus': {
        '_get': 51,     # from com.libratone.model.LSSDPNode, fetchPlayStatus
        # from com.libratone.luci.PlayControlCommand - more state are defined
        'play': b'0',
        'stop': b'1',
        'pause': b'2',
    },
    'Volume': {
        '_get': 64,     # from com.libratone.model.LSSDPNode, fetchVolume
        '_set': 64,     # from com.libratone.model.LSSDPNode, setVolume
    },
    'Player': {
        '_set': 277,    # from com.libratone.model.LSSDPNode, setPlayer
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
        '_get': 516,    # from com.libratone.model.LSSDPNode, fetchVoicing
        '_set': 518,    # from com.libratone.model.LSSDPNode, setVoicing
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
        # Used for trigger
        '_get': 1284,   # from com.libratone.model.LSSDPNode, fetchChargingStatus
    },
}

# Check if host is up
def host_up(host, port=80):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
    except socket.error:
        return False
    sock.close()
    del sock
    return True

class LibratoneZipp:
    """Representing a Libratone Zipp device."""

    # host is IP of Zipp
    def __init__(self, host, name="Zipp"):

        # TODO Publish all variables

        # Configuration set by class client
        self.host = host
        self.name = name
        
        # Variables fixed for the lifecycle
        self.version = None
        
        # Active variables
        self._voicing_raw = None # V10x-like codes
        self.volume = None
        self.chargingstatus = None
        self.powermode = None

        # Calculated variables
        self.state = None                               # STATE_OFF in self.state_refresh() or STATE_PLAY/STOP/PAUSE in process_zipp_message() initiated from 
        self.voicing = None                             # 'name' are used: "Neutral", "Easy Listening", ...
        self.voicing_list = self.voicing_list_define()

        # Network

        ## Setup 1st thread to monitor _UDP_NOTIFICATION_RECEIVE_PORT = 3333, where Zipp send notifications proactively, after an initial trigger and if ACK are send for every packet
        self._listening_notification_flag = True   # Flag to shut down the thread
        self._listening_notification_socket, self._listening_notification_thread = self._get_new_socket(receive_port=_UDP_NOTIFICATION_RECEIVE_PORT, trigger_port=_UDP_CONTROL_PORT, ack_port=_UDP_NOTIFICATION_SEND_PORT)

        ## Setup 2nd thread to monitor _UDP_RESULT_PORT = 7778, where Zipp answer request made to _UDP_CONTROL_PORT = 7777
        self._listening_result_flag = True
        self._listening_result_socket, self._listening_result_thread = self._get_new_socket(receive_port=_UDP_RESULT_PORT)

        ## Setup 3rd thread to make regular call to Zipp in order to update status in case of desync
        self._keepalive_flag = True
        self._keepalive_thread = threading.Thread(target=self._keepalive_check, name="Zipp_keepalive", args=[])
        self._keepalive_thread.start()

    # Close the two socket thread by changing the flag and sending two packet to receive two answer on 2 ports
    def exit(self):
        self._listening_notification_flag = False
        self.set_control_command(command=_COMMAND_TABLE['Volume']['_set'], data=self.volume)
        self._listening_result_flag = False
        self.get_control_command(command=_COMMAND_TABLE['Version']['_get'])
        self._keepalive_thread = False
        _LOGGER.info("Disconnected from Libratone Zipp, waiting for last packets.")

    # Do a state_refresh every _KEEPALIVE_CHECK_PERIOD seconds to update self.state
    def _keepalive_check(self):
        while(self._keepalive_flag):
            self.state_refresh()
            time.sleep(_KEEPALIVE_CHECK_PERIOD)
        _LOGGER.info("Keep-alive thread closed.")

    # Interpret message from Zipp
    def process_zipp_message(self, packet: bytearray):
        
        zipp_message = LibratoneMessage.LibratoneMessage(packet=packet)
        command = zipp_message.get_command_int()
        data = zipp_message.data

        if command == 0: pass
        elif command == _COMMAND_TABLE['Voicing']['_get']:
            self._voicing_raw = data.decode()
            self._voicing_update_from_raw()
        elif command == _COMMAND_TABLE['PlayStatus']['_get']:
            if data == _COMMAND_TABLE['PlayStatus']['play']: self.state = STATE_PLAY
            elif data == _COMMAND_TABLE['PlayStatus']['stop']: self.state = STATE_STOP
            elif data == _COMMAND_TABLE['PlayStatus']['pause']: self.state = STATE_PAUSE
        elif command == _COMMAND_TABLE['Version']['_get']: self.version = data.decode()
        elif command == _COMMAND_TABLE['Volume']['_get']: self.volume = data.decode()
        elif command == _COMMAND_TABLE['ChargingStatus']['_get']: self.chargingstatus = data.decode()
        elif command == _COMMAND_TABLE['PowerMode']['_get']: self.powermode = data.decode()
        else:
            if _LOG_UNKNOWN_PACKET:
                try: pretty_data = data.decode()
                except: pretty_data = data
                _LOGGER.info("\nCOMMAND:", command, "DATA:", pretty_data)
            else: pass

    # Wait for a message from the Zipp, start a thread to process it and send an ACK to _UDP_NOTIFICATION_SEND_PORT = 3334
    def listen_incoming_zipp_notification(self, socket, receive_port, ack_port=None):
        _LOGGER.info("Listening incoming Zipp messages on %s", str(receive_port))
        while(self._listening_notification_flag):
            # Wait for new packet; address is the originating IP:port
            try:
                message, address = socket.recvfrom(_UDP_BUFFER_SIZE)
                thread = threading.Thread(target=self.process_zipp_message, name="Process_Zipp_Message", args=[message])
                thread.start()

                # Send the ack
                if ack_port != None: socket.sendto(LibratoneMessage.LibratoneMessage(command=0).get_packet(), (self.host, _UDP_NOTIFICATION_SEND_PORT))
            except:
                _LOGGER.info("Connection closed! Port %s", str(receive_port))
                self.state = STATE_OFF
                self.version = None
                self._voicing_raw = None 
                self.volume = None
                self.chargingstatus = None
                self.powermode = None
                self.voicing = None
                while(self.state == STATE_OFF):
                    time.sleep(_KEEPALIVE_CHECK_PERIOD)

    # Create a socket, start a thread to manage incoming messages from receive_port and send a trigger to trigger_port
    def _get_new_socket(self, receive_port, trigger_port=None, ack_port=None):
        try:
            _new_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

            # Instanciate a thread to manage incoming messages
            _new_thread = threading.Thread(target=self.listen_incoming_zipp_notification,  name="Listen_incoming_"+str(receive_port), args=[_new_socket, receive_port, ack_port])
            _new_thread.start()

            # Set up a listening socker
            _new_socket.bind(("", receive_port))

            if trigger_port != None:
                # Send trigger
                _new_socket.sendto(LibratoneMessage.LibratoneMessage(command=_COMMAND_TABLE['ChargingStatus']['_get']).get_packet(), (self.host, trigger_port))

            # TODO Maybe a keep-alive thread (send ba_ack every 10 min) will be needed
            return _new_socket, _new_thread

        except ConnectionError as connection_error:
            _LOGGER.warning("Connection error: %s", connection_error)
            return None
        except socket.gaierror as socket_gaierror:
            _LOGGER.warning("Address-related error: %s", socket_gaierror)
            return None
        except socket.error as socket_error:
            _LOGGER.warning("Socket error: %s", socket_error)
            return None

    # Send a defined message to the zipp at a defined port
    def send_command(self, port, command, commandType = None, data = None):
        if self._listening_notification_socket is None:
            self._listening_notification_socket = self._get_new_socket()

        try:
            # Generate the message
            message = LibratoneMessage.LibratoneMessage(command=command, data=data, commandType=commandType).get_packet()

            # Send a store the answer in resp
            resp = self._listening_notification_socket.sendto(message, (self.host, port))

            if resp == 0:
                self._listening_notification_socket.close()
                self._listening_notification_socket = None
                _LOGGER.warning("Send fail, disconnecting socket")
            else:
                return True

        except (BrokenPipeError, ConnectionError) as connect_error:
            _LOGGER.warning("Connection error, retrying. %s", connect_error)
            self._listening_notification_socket = None
            self._listening_notification_socket = self._get_new_socket(self.host, port)
            if self._listening_notification_socket is not None:
                # retrying after broken pipe error
                self._listening_notification_socket.sendto(message, (self.host, port))
    
    # Send a control message to set something (port _UDP_CONTROL_PORT = 7777) - Use the send_command function
    def set_control_command(self, command, data = None):
        return self.send_command(port=_UDP_CONTROL_PORT, command=command, data=data)

    # Send a control message to get something - same than above
    def get_control_command(self, command, data = None):
        return self.send_command(port=_UDP_CONTROL_PORT, command=command, data=data, commandType=1)

    # Get functions to get status - assuming that the speaker will answer it
    def version_get(self): return self.get_control_command(command=_COMMAND_TABLE['Version']['_get'])
    def volume_get(self): return self.get_control_command(command=_COMMAND_TABLE['Volume']['_get'])
    def voicing_get(self): return self.get_control_command(command=_COMMAND_TABLE['Voicing']['_get'])
    def chargingstatus_get(self): return self.get_control_command(command=_COMMAND_TABLE['ChargingStatus']['_get'])
    def playstatus_get(self): return self.get_control_command(command=_COMMAND_TABLE['PlayStatus']['_get'])
    
    # Call all *get* functions above
    def get_all(self):
        self.version_get()
        self.chargingstatus_get()
        self.volume_get()
        self.voicing_get()
        self.playstatus_get()

    # Refresh the state of the Zipp
    def state_refresh(self):
        if host_up(self.host):
            self.get_all()
        else: self.state = STATE_OFF

    # Send PlayControl commands
    def _playcontrol_set(self, action):
        # Possible actions are defined in _COMMAND_TABLE['PlayControl']
        try:
            self.set_control_command(_COMMAND_TABLE['PlayControl']['_set'], _COMMAND_TABLE['PlayControl'][action])
            return True
        except:
            _LOGGER.warning("Error: %s command not sent.", action)
            return False
    def play(self): return self._playcontrol_set('play')
    def pause(self): return self._playcontrol_set('pause')
    def stop(self): return self._playcontrol_set('stop')
    def next(self): return self._playcontrol_set('next')
    def prev(self): return self._playcontrol_set('prev')

    # Send PowerMode commands
    def _powermode_set(self, action): 
         # Possible actions are defined in _COMMAND_TABLE['PowerMode']
        try:
            self.set_control_command(_COMMAND_TABLE['PowerMode']['_set'], _COMMAND_TABLE['PowerMode'][action])
            return True
        except:
            _LOGGER.warning("Error: %s command not sent.", action)
            return False
    def sleep(self): return self._powermode_set('sleep')
    def wakeup(self): return self._powermode_set('wakeup')

    # Send Player-Favorite command
    def favorite_play(self, favourite_id):
        if int(favourite_id) < 1 or int(favourite_id) > 5:
            _LOGGER.warning("Error: favorite command must be within 1 and 5.")
            return False
        try:
            if not isinstance(favourite_id, str): favourite_id = str(favourite_id)
            self.set_control_command(_COMMAND_TABLE['Player']['_set'], _COMMAND_TABLE['Player']['favorite'][favourite_id])
            return True
        except:
            _LOGGER.warning("Error: favorite command not sent.")
            return False

    # Send Voicing command
    def voicing_set(self, voicing_id:str):
        try:
            for item in _COMMAND_TABLE['Voicing']:
                if item != '_set' and item != '_get' and voicing_id == _COMMAND_TABLE['Voicing'][item]['name']:
                    self.set_control_command(_COMMAND_TABLE['Voicing']['_set'], _COMMAND_TABLE['Voicing'][item]['_data'])
                    break
            return True
        except:
            _LOGGER.warning("Error: voicing command not sent.")
            return False

    # Send list of all voicing in "Name" format
    def voicing_list_define(self):
        list = []
        for item in _COMMAND_TABLE['Voicing']:
            if item != '_set' and item != '_get':
                list.append(_COMMAND_TABLE['Voicing'][item]['name'])
        return list

    # Transform raw voicing (V10x codes) into 
    def _voicing_update_from_raw(self):
        for item in _COMMAND_TABLE['Voicing']:
            if item != '_set' and item != '_get':
                if self._voicing_raw == _COMMAND_TABLE['Voicing'][item]['_data']:
                    self.voicing = _COMMAND_TABLE['Voicing'][item]['name']
                    return True

    # Send Volume command
    def volume_set(self, volume):
        if int(volume) < 0 or int(volume) > 100:
            _LOGGER.warning("Error: volume command must be within 0 and 100.")
            return False
        try:
            # if volume is a string
            if isinstance(volume, str): self.set_control_command(_COMMAND_TABLE['Volume']['_set'], volume)
            else: self.set_control_command(_COMMAND_TABLE['Volume']['_set'], str(volume))
            return True
        except:
            _LOGGER.warning("Error: volume command not sent.")
            return False

    