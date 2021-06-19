#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Control Library for Libratone speakers like Libratone Zipp.
License: see LICENSE file
"""

import logging
import json
import sys
import time
import socket
import threading
from . import LibratoneMessage

_GET_LIFECYCLE_VALUES = 1       # 3 seconds wait between asking lifecycle values (like all voicing) and asking current values(like voicing)

_LOG_ALL_PACKET = False          # Log all packet
_LOG_UNKNOWN_PACKET = True     # Log unknown packet
_LOGGER_PRINT = True            # Redirect logger to stdout, otherwise standard Home Assistant logger

if _LOGGER_PRINT:
    _log_level=logging.DEBUG 
    _log_format = logging.Formatter('[%(asctime)s] [%(levelname)s] - %(message)s')
    _LOGGER = logging.getLogger(__name__)                                  
    _LOGGER.setLevel(_log_level)                                       

    # writing to stdout                                                     
    handler = logging.StreamHandler(sys.stdout)                             
    handler.setLevel(_log_level)                                        
    handler.setFormatter(_log_format)                                        
    _LOGGER.addHandler(handler)                                            

    _LOGGER.debug("Logging has been setup")                                                   
else:
    _LOGGER = logging.getLogger("LibratoneZipp")

# Define fixed variables
STATE_UNKOWN = "UNKOWN"
STATE_SLEEP = "SLEEPING"
STATE_ON = "ON"
STATE_PLAY = "PLAYING"
STATE_PAUSE = "PAUSED"
STATE_STOP = "STOPPED"

POWERMODE_AWAKE = "AWAKE"
POWERMODE_SLEEP = "SLEEP"

PLAYSTATUS_PLAY = STATE_PLAY
PLAYSTATUS_PAUSE = STATE_PAUSE
PLAYSTATUS_STOP = STATE_STOP

# Define network variables
_UDP_CONTROL_PORT = 7777                 # Port to send a command
_UDP_RESULT_PORT = 7778                  # Port to receive the result of a command??
_UDP_NOTIFICATION_SEND_PORT = 3334       # Port to send ack to the speaker after a notification
_UDP_NOTIFICATION_RECEIVE_PORT = 3333    # Port to receive notification from the speaker

_UDP_BUFFER_SIZE = 4096                 # 4096 in order to receive Channel data
_KEEPALIVE_CHECK_PERIOD = 30            # Time in second between each keep-alive check 

# Define Zipp commands ID
_COMMAND_TABLE = {
    # com.libratone.model.LSSDPNode , fetchAllForWifi contain all useful fonctions 
    'Version': {
        '_get': 5,      # from com.libratone.model.LSSDPNode, fetchVersion
    },
    'CurrPowerMode': {
        '_get': 14,     # from com.libratone.model.LSSDPNode, fetchCurrPowerMode - reply in dec, not ASCII - see _currpowermode_parsing 
        'awake': 48,    # from observation
        'sleeping': 50, # from observation
    },
    'Timer': {
        # Used for sleep timer
        '_get': 15,     # from com.libratone.model.LSSDPNode, setOffTime - format for timer data is "2" + j, j being seconds      
        '_set': 15,     # from com.libratone.model.LSSDPNode, setPowerMode - see _timer_parse for parsing 
    },
    'PlayControl': {
        '_set': 40,     # # from com.libratone.model.LSSDPNode, setPlayControl - see below for data
        # from com.libratone.luci.PlayControlCommand
        'play': 'PLAY',
        'stop': 'STOP',
        'pause': 'PAUSE',
        'next': 'NEXT',
        'prev': 'PREV',
    },
    'PlayStatus': {
        '_get': 51,     # from com.libratone.model.LSSDPNode, fetchPlayStatus - see below for data
        # from com.libratone.luci.PlayControlCommand - more state are defined
        'play': b'0',
        'stop': b'1',
        'pause': b'2',
    },
    'Volume': {
        '_get': 64,     # from com.libratone.model.LSSDPNode, fetchVolume
        '_set': 64,     # from com.libratone.model.LSSDPNode, setVolume - expect data with volume 0...100
    },
    'Name': {
        '_get': 90,     # from com.libratone.model.LSSDPNode, fetchDeviceName
        '_set': 90,     # from com.libratone.model.LSSDPNode, setName - expect data with wished device name
    },
    'BatteryLevel': {
        '_get': 256,     # from com.libratone.model.LSSDPNode, fetchBatteryLevel - answer "" on _get, true vale on _get2
        '_get2': 257,    # Received when BatteryLevel_get is sent - answer "59" for instance
    },
    'Channel': {
        '_get': 275,     # from com.libratone.model.LSSDPNode, fetchChannel - answer JSON like [{"channel_id" : 1,"channel_identity" : "31375","channel_name" : "Radio Meuh","channel_type" : "vtuner","isPlaying" : false,"play_token" : ""}, ...]
    },
    'Player': {
        '_get': 278,    # from com.libratone.model.LSSDPNode, fetchPlayer
        '_set': 277,    # from com.libratone.model.LSSDPNode, setPlayer - see below for data
        # Favorites, captured:
        # TODO check play_identity 
        'favorite': {
            '1': '{"isFromChannel":false,"play_identity":"1","play_subtitle":"1","play_title":"channel","play_type":"channel","token":""}',
            '2': '{"isFromChannel":false,"play_identity":"2","play_subtitle":"2","play_title":"channel","play_type":"channel","token":""}',
            '3': '{"isFromChannel":false,"play_identity":"2","play_subtitle":"3","play_title":"channel","play_type":"channel","token":""}',
            '4': '{"isFromChannel":false,"play_identity":"2","play_subtitle":"4","play_title":"channel","play_type":"channel","token":""}',
            '5': '{"isFromChannel":false,"play_identity":"2","play_subtitle":"5","play_title":"channel","play_type":"channel","token":""}',
        },
    },
    'Voicing': {
        '_get': 516,    # from com.libratone.model.LSSDPNode, fetchVoicing - you'll get a V100-like code
        '_set': 518,    # from com.libratone.model.LSSDPNode, setVoicing - see below for data in '_data' like V100
        '_getAll': 524, # from com.libratone.model.LSSDPNode, fetchAllVoicing - you'll get a JSON like [{"description":"Basic neutral setting","name":"Neutral","voicingId":"V100"}, ...]
    },
    'Room': {
        '_get': 517,    # from com.libratone.model.LSSDPNode, fetchFullroom - will return a voicingId defined in getAll like "neutral"
        '_set': 519,    # from com.libratone.model.LSSDPNode, setFullRoom - expect a voicingId defined in getAll like "neutral"
        '_getAll': 525, # from com.libratone.model.LSSDPNode, fetchAllFullRoom - will return a JSON like [{"description":"Basic neutral setting","name":"Neutral","voicingId":"neutral"}, ...]
    },
    'MuteStatus': {
        '_get': 520     # from com.libratone.model.LSSDPNode, fetchMuteStatus - answer "UNMUTE" for instance
    },
    'SignalStrength': {
        '_get': 529     # from com.libratone.model.LSSDPNode, fetchSignalStrength - answer "-86,-42,5/5" for instance
    },
    'SerialNumber': {
        '_get': 769     # from com.libratone.model.LSSDPNode, fetchSerialNum - answer "1234-A1234567-12-12345" for instance
    },
    'DeviceColor': {
        '_get': 770,     # from com.libratone.model.LSSDPNode, fetchDeviceColor - answer "1001" for instance for Pepper Black and "2005" for Sangria
        '_set': 771     # from com.libratone.model.LSSDPNode, setDeviceColor - answer "1001" for instance for Pepper Black and "2005" for Sangria
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
    def __init__(self, host):

        # Configuration set by class client
        self.host = host
        
        # TODO Update all variables to be set to Null when disconnect

        # Variables fixed for the lifecycle
        self.version = None
        self.name = None
        self.serialnumber = None
        
        # Active variables
        self._currpowermode = None
        self._playstatus = None
        self.volume = None
        self.batterylevel = None
        self.chargingstatus = None
        self.timer = None           # Timer in seconds, None if no timers active
        self.signalstrenght = None
        self.devicecolor = None
        self.mutestatus = None

        # Active variables as JSON list - see command table
        self._voicing_list_json = None   
        self._room_list_json = None      
        self._player_json = None
        self._channel_json = None

        # Calculated variables
        self.state = None               # STATE_OFF in self.state_refresh() or STATE_PLAY/STOP/PAUSE in process_zipp_message() initiated from 
        self.room = None                # voicingId converted to Name for Room
        self.voicing = None             # voicingId converted to Name for Voicing
        self.room_list = None           # List of Room "name"
        self.voicing_list = None        # List of Voicing "name"
        # Variables from Player
        self.isFromChannel = None
        self.play_identity = None
        self.play_preset_available = None
        self.play_subtitle = None
        self.play_title = None
        self.play_token = None
        self.play_type = None

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

    # Log messgaes in a pretty way
    def log_zipp_messages(self, command, data, port):
        try: pretty_data = data.decode()
        except: pretty_data = data
        _LOGGER.info("Port:" + str(port) + " Command:" + str(command) + "\tData:" + str(pretty_data))

    # Interpret message from Zipp
    def process_zipp_message(self, packet: bytearray, receive_port):
        
        zipp_message = LibratoneMessage.LibratoneMessage(packet=packet)
        command = zipp_message.get_command_int()
        data = zipp_message.data

        if _LOG_ALL_PACKET: self.log_zipp_messages(command=command, data=data, port=receive_port)

        if command == 0: pass
        elif command == _COMMAND_TABLE['PlayStatus']['_get']:
            if data == _COMMAND_TABLE['PlayStatus']['play']: self._playstatus = PLAYSTATUS_PLAY
            elif data == _COMMAND_TABLE['PlayStatus']['stop']: self._playstatus = PLAYSTATUS_STOP
            elif data == _COMMAND_TABLE['PlayStatus']['pause']: self._playstatus = PLAYSTATUS_PAUSE
            self._state_calculate()
        elif command == _COMMAND_TABLE['CurrPowerMode']['_get']:
            if data[0] == _COMMAND_TABLE['CurrPowerMode']['awake']: self._currpowermode = POWERMODE_AWAKE
            elif data[0] == _COMMAND_TABLE['CurrPowerMode']['sleeping']: self._currpowermode = POWERMODE_SLEEP
            self._state_calculate()
        elif command == _COMMAND_TABLE['Channel']['_get']:
            try: self._channel_json = json.loads(data.decode())
            except: self._channel_json = None
        elif command == _COMMAND_TABLE['Voicing']['_get'] or command == _COMMAND_TABLE['Voicing']['_set']: self.voicing = self._voicingid_to_name(voicingid=data.decode(), json_list=self._voicing_list_json)
        elif command == _COMMAND_TABLE['Room']['_get'] or command == _COMMAND_TABLE['Room']['_set']: self.room = self._voicingid_to_name(voicingid=data.decode(), json_list=self._room_list_json)
        elif command == _COMMAND_TABLE['Voicing']['_getAll']: self._voicing_list_update_from_raw(data.decode())
        elif command == _COMMAND_TABLE['Room']['_getAll']: self._room_list_update_from_raw(data.decode())
        elif command == _COMMAND_TABLE['Player']['_get']: self._player_parse(player_data=data.decode())
        elif command == _COMMAND_TABLE['Timer']['_get']: self.timer = self._timer_parse(data)
        elif command == _COMMAND_TABLE['Name']['_get']: self.name = data.decode()
        elif command == _COMMAND_TABLE['Version']['_get']: self.version = data.decode()
        elif command == _COMMAND_TABLE['Volume']['_get']: self.volume = data.decode()
        elif command == _COMMAND_TABLE['ChargingStatus']['_get']: self.chargingstatus = data.decode()
        elif command == _COMMAND_TABLE['SignalStrength']['_get']: self.signalstrenght = data.decode()
        elif command == _COMMAND_TABLE['SerialNumber']['_get']: self.serialnumber = data.decode()
        elif command == _COMMAND_TABLE['MuteStatus']['_get']: self.mutestatus = data.decode()
        elif command == _COMMAND_TABLE['DeviceColor']['_get'] or command == _COMMAND_TABLE['DeviceColor']['_set']: self.devicecolor = data.decode()
        elif command == _COMMAND_TABLE['BatteryLevel']['_get'] or command == _COMMAND_TABLE['BatteryLevel']['_get2']: self.batterylevel = data.decode()
        else:
            if _LOG_UNKNOWN_PACKET: self.log_zipp_messages(command=command, data=data, port=receive_port)
            else: pass

    # Wait for a message from the Zipp, start a thread to process it and send an ACK to _UDP_NOTIFICATION_SEND_PORT = 3334
    def listen_incoming_zipp_notification(self, socket, receive_port, ack_port=None):
        _LOGGER.info("Listening incoming Zipp messages on %s", str(receive_port))
        while(self._listening_notification_flag):
            # Wait for new packet; address is the originating IP:port
            try:
                message, address = socket.recvfrom(_UDP_BUFFER_SIZE)
                thread = threading.Thread(target=self.process_zipp_message, name="Process_Zipp_Message", args=[message, receive_port])
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
                self.timer = None
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
    def name_get(self): return self.get_control_command(command=_COMMAND_TABLE['Name']['_get'])
    def volume_get(self): return self.get_control_command(command=_COMMAND_TABLE['Volume']['_get'])
    def voicing_get(self): return self.get_control_command(command=_COMMAND_TABLE['Voicing']['_get'])
    def chargingstatus_get(self): return self.get_control_command(command=_COMMAND_TABLE['ChargingStatus']['_get'])
    def playstatus_get(self): return self.get_control_command(command=_COMMAND_TABLE['PlayStatus']['_get'])
    def room_getall(self): return self.get_control_command(command=_COMMAND_TABLE['Room']['_getAll'])
    def voicing_getall(self): return self.get_control_command(command=_COMMAND_TABLE['Voicing']['_getAll'])
    def room_get(self): return self.get_control_command(command=_COMMAND_TABLE['Room']['_get'])
    def player_get(self): return self.get_control_command(command=_COMMAND_TABLE['Player']['_get'])
    def signalstrenght_get(self): return self.get_control_command(command=_COMMAND_TABLE['SignalStrength']['_get'])
    def devicecolor_get(self): return self.get_control_command(command=_COMMAND_TABLE['DeviceColor']['_get'])
    def serialnumber_get(self): return self.get_control_command(command=_COMMAND_TABLE['SerialNumber']['_get'])
    def mutestatus_get(self): return self.get_control_command(command=_COMMAND_TABLE['MuteStatus']['_get'])
    def batterylevel_get(self): return self.get_control_command(command=_COMMAND_TABLE['BatteryLevel']['_get'])
    def channel_get(self): return self.get_control_command(command=_COMMAND_TABLE['Channel']['_get'])
    def timer_get(self): return self.get_control_command(command=_COMMAND_TABLE['Timer']['_get'])
    def currpowermode_get(self): return self.get_control_command(command=_COMMAND_TABLE['CurrPowerMode']['_get'])
    
    # Call all *get* functions above, except fixed values
    def get_all(self):
        self.currpowermode_get()
        self.chargingstatus_get()
        self.volume_get()
        self.voicing_get()
        self.room_get()
        self.player_get()
        self.signalstrenght_get()
        self.mutestatus_get()
        self.batterylevel_get()
        self.timer_get()
        self.playstatus_get()

    # Call all *get* for values that are fixed for the lifecycle 
    def get_all_fixed_for_lifecycle(self):
        self.currpowermode_get()
        self.version_get()
        self.name_get()
        self.room_getall()
        self.voicing_getall()
        self.devicecolor_get()
        self.serialnumber_get()
        self.channel_get()

    # Calculate Zipp state based on _currpowermode and _playstatus
    def _state_calculate(self):
        # If the Zipp sleeps, set this status
        if self._currpowermode == POWERMODE_SLEEP:
            self.state = STATE_SLEEP
            return True
        elif self._currpowermode == POWERMODE_AWAKE:
            if self._playstatus == PLAYSTATUS_PLAY: self.state = STATE_PLAY
            elif self._playstatus == PLAYSTATUS_PAUSE: self.state = STATE_PAUSE
            elif self._playstatus == PLAYSTATUS_STOP: self.state = STATE_STOP
            else:
                self.state = STATE_ON
                return True
        else:
            self.state = STATE_UNKOWN
            return False


    # Refresh the state of the Zipp
    def state_refresh(self):
        if host_up(self.host):
            # If the Zipp was not in a "controlled" state, refresh also lifecycle variables
            if self.state != STATE_PLAY and self.state != STATE_PAUSE and self.state != STATE_STOP:
                self.get_all_fixed_for_lifecycle()
                time.sleep(_GET_LIFECYCLE_VALUES)
            self.get_all()
        else: self.state = STATE_UNKOWN

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

    # Define a name
    def name_set(self, name:str): return self.set_control_command(command=_COMMAND_TABLE['Name']['_set'], data=str(name))


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

    # Send a voicingid, either for type="Voicing" or type="Room"
    def _voicingid_set(self, voicing_name, type):

        if type != "Voicing":
            json_list = self._voicing_list_json
        elif type != "Room":
            json_list = self._room_list_json
        else:
            _LOGGER.warning("voicingid_set: type must be either 'Voicing' or 'Room'")
            return False
        
        try:
            for item in json_list:
                if voicing_name == item['name']:
                    self.set_control_command(command=_COMMAND_TABLE[type]['_set'], data=item['voicingId'])
                    break
            return True
        except:
            _LOGGER.warning("Error: voicing command not sent.")
            return False

    # Send Voicing command
    def voicing_set(self, voicing_name:str): return self._voicingid_set(voicing_name=voicing_name, type="Voicing")
    def room_set(self, room_name:str): return self._voicingid_set(voicing_name=room_name, type="Voicing")


    # Transform raw all room/voicing list (JSON) into a list with only room names
    def _name_list_from_json(self, json_list):
        name_list = []
        for item in json_list:
            name_list.append(item['name'])
        return name_list

    # Parse raw voicing list, update the name list
    def _voicing_list_update_from_raw(self, raw_list):
        try:
            self._voicing_list_json = json.loads(raw_list)
            self.voicing_list = self._name_list_from_json(self._voicing_list_json)
        except:
            self._voicing_list_json = None
            self.voicing_list = None

    # Parse raw room list, update the name list
    def _room_list_update_from_raw(self, raw_list):
        try:
            self._room_list_json = json.loads(raw_list)
            self.room_list = self._name_list_from_json(self._room_list_json)
        except:
            self._room_list_json = None
            self.room_list = None

    # Transform a raw voicingId (used by both Voicing and Room) into Name
    def _voicingid_to_name(self, voicingid, json_list):
        if json_list == None:
            _LOGGER.error("Cannot parse " + voicingid + " as JSON list is empty.")
            return None
        try:
            for item in json_list:
                if voicingid == item['voicingId']:
                    return item['name']
        except:
            return None

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

    # Parse Player data: populate all play_* variables
    def _player_parse(self, player_data):
        try:
            self._player_json = json.loads(player_data)
            self.isFromChannel = self._player_json['isFromChannel']
            self.play_identity = self._player_json['play_identity']
            self.play_preset_available = self._player_json['play_preset_available']
            self.play_subtitle = self._player_json['play_subtitle']
            self.play_title = self._player_json['play_title']
            self.play_token = self._player_json['play_token']
            self.play_type = self._player_json['play_type']
        except:
            self._player_json = None
            self.isFromChannel = None
            self.play_identity = None
            self.play_preset_available = None
            self.play_subtitle = None
            self.play_title = None
            self.play_token = None
            self.play_type = None

    # Parse Timer, return *DEFINED* timer in second, not the actual one which is running!
    def _timer_parse(self, timer_data):
        if timer_data == b'': return None
        elif timer_data[0] == 255: return None  # Always the case when no timer is defined
        elif timer_data[0] == 50:   # Always when there's an active timer
            return timer_data[1] + timer_data[2]*256
        else:
            return None

    # Send timer commands - timer is in seconds
    def timer_set(self, timer): return self.set_control_command(command=_COMMAND_TABLE['Timer']['_set'], data="2"+str(timer))
    def sleep(self): return self.timer_set(0)
    def wakeup(self): return self.set_control_command(command=_COMMAND_TABLE['Timer']['_set'], data="F0")
