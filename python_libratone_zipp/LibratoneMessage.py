import random

'''
This class provide an object to manage, set and create messages that can be sent to a Libratone Zipp device.

Usage:
m = LibratoneMessage.LibratoneMessage()     | Create a new object, can contain `command` and `data`
m.set_packet(bytearray_message)             | Parse the content of a received Zipp message into the object
m.set_command(40)                           | Set the command byte, here to "40"
m.set_data("PLAY")                          | Set the data bytes, here to "PLAY"
m.get_packet()                              | Receive a message ready to be sent
m.print_packet()                            | Print every property of the Zipp message

Message are mainly based upon decompilation of the Android application (com.libratone.luci.LUCIPacket)

Example of a message: 0xaaaa??abcd??abcdabcdxxx
0x  aaaa??abcd??abcdabcdxxx
0x  aaaa................... = Remote ID = 43690 for the Android device
    ....??................. = CommandType = b if available, or 2 by default
    ......abcd............. = Command
    ..........??........... = CommandStatus = 0 but can be set with setCommandStatus
    ............abcd....... = nextInt = CRC = Random().nextInt(65534) + 1
    ................abcd... = DataLen = data.lenght
    ....................xxx = data
'''

class LibratoneMessage:
    def __init__(self, command:int = None, data:str = None, packet:bytearray = None, commandType:int = None, commandStatus:int = None):
        # Initialization with default values
        self.remoteID = bytearray([0xaa, 0xaa])                     # Hardcoded in Android app
        self.commandType = bytearray([0x02])                        # 2 by default (get), probably 0x01 for fetch
        self.command = bytearray([0x00, 0x00])                      # See _COMMAND_TABLE[*command*][_command]
        self.commandStatus = bytearray([0x00])                      # 0 but can be set with setCommandStatus in Android app
        self.crc = random.randint(1,65535).to_bytes(2, 'big')       # Hardcoded in Android app
        self.datalen = bytearray([0x00, 0x00])                      # Lenght of `data`, in byte
        self.data = None                                           # See _COMMAND_TABLE[*command*][data]

        if command != None: self.set_command(command)
        if data != None: self.set_data(data)
        if packet != None: self.set_from_packet(packet)
        if commandType != None: self.set_commandType(commandType)
        if commandStatus != None: self.set_commandStatus(commandStatus)

    # Return packet content as bytearray
    def get_packet(self):
        if self.data == None: return self.remoteID + self.commandType + self.command + self.commandStatus + self.crc + self.datalen
        else: return self.remoteID + self.commandType + self.command + self.commandStatus + self.crc + self.datalen + self.data
    
    # Receive a packet content
    def set_from_packet(self, packet:bytearray):
        # Extra `to-byte` because I don't manage it that well
        # slice(start, end) with end the OUTBOUND limit (= not included)
        self.remoteID = packet[slice(0,2)]
        self.commandType = packet[2].to_bytes(1, 'big')
        self.command = packet[3] << 8 | packet[4]
        self.command = self.command.to_bytes(2, 'big')
        self.commandStatus = packet[5].to_bytes(1, 'big')
        self.crc = packet[slice(6,8)]
        self.datalen = packet[slice(8,10)]
        self.data = packet[slice(10,len(packet))]
        return self.command, self.data
    
    def set_commandType(self, commandType:int):
        self.commandType = commandType.to_bytes(1, 'big')
        return True

    def set_command(self, command:int):
        self.command = command.to_bytes(2, 'big')
        return True

    def set_commandStatus(self, commandStatus:int):
        self.commandStatus = commandStatus.to_bytes(2, 'big')
        return True

    # Set a data content along with the correct dataLen
    def set_data(self, data:bytearray):
        self.datalen = len(data).to_bytes(2, 'big')
        self.data = bytes(data, "ascii")  
        return True  

    # Return various data  as an int format
    def get_commandType_int(self): return self.commandType[0]
    def get_command_int(self): return self.command[0]*256 + self.command[1]
    def get_commandStatus_int(self): return self.commandStatus[0]

    # Print packet content for debug purpose
    def print_packet(self):
        print("remoteID", self.remoteID)
        print("commandType", self.commandType)
        print("command", self.command)
        print("commandStatus", self.commandStatus)
        print("crc", self.crc)
        print("dataLen", self.datalen)
        print("data", self.data)
        print("FULL MESSAGE", self.get_packet())
