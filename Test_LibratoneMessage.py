from python_libratone_zipp import LibratoneMessage

# New packet to send PLAY
message = LibratoneMessage.LibratoneMessage(packet=bytearray([
    0x00, 0x00, # remoteID
    0x02,       # commandType
    0x02, 0x04, # command
    0x00,       # commandStatus
    0x00, 0x00, # crc
    0x00, 0x04, # datalen
    0x50, 0x4c, 0x41, 0x59]))

# message = LibratoneMessage.LibratoneMessage(516)

message.print_packet()
print(message.get_command_int())
print(message.get_commandType_int())