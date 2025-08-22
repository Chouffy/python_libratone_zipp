#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Command-Line Interface for the `python_libratone_zipp` module.
"""

from python_libratone_zipp import LibratoneZipp

zipp1 = LibratoneZipp(host='192.168.188.154')
zipp2 = LibratoneZipp(host="192.168.188.40")

speakers = [zipp1, zipp2]

while True:
    zipp = speakers[int(input(f"input the desired speaker: 1-{len(speakers)}")) - 1]
    user_choice = input("Input your command: play, pause, stop, next, prev, sleep, wakeup, fav_play, player, voicing, room, volume, name_set, info, channel, timer, exit? ")

    if user_choice == "play": zipp.play()
    elif user_choice == "pause": zipp.pause()
    elif user_choice == "stop": zipp.stop()
    elif user_choice == "next": zipp.next()
    elif user_choice == "prev": zipp.prev()
    elif user_choice == "sleep": zipp.sleep()
    elif user_choice == "wakeup": zipp.wakeup()

    elif user_choice == "fav_play": zipp.favorite_play(input("Input favorite ID: 1, 2, ... 5? "))
    elif user_choice == "volume": zipp.volume_set(input("Input volume 0...100? "))
    elif user_choice == "name_set": zipp.name_set(input("Input device name? "))

    elif user_choice == "voicing":
        print("\nList of voicing:")
        print(*zipp.voicing_list, sep= ", ")
        if zipp.voicing != None: print("Current voicing:", zipp.voicing)
        zipp.voicing_set(input("\nInput voicing name, not ID: "))

    elif user_choice == "room":
        print("\nList of room:")
        print(*zipp.room_list, sep= ", ")
        if zipp.room != None: print("Current room:", zipp.room)
        zipp.room_set(input("\nInput room setting name, not ID: "))

    elif user_choice == "player":
        if zipp.isFromChannel != None: print("isFromChannel:", zipp.isFromChannel)
        if zipp.play_identity != None: print("play_identity:", zipp.play_identity)
        if zipp.play_preset_available != None: print("play_preset_available:", zipp.play_preset_available)
        if zipp.play_subtitle != None: print("play_subtitle:", zipp.play_subtitle)
        if zipp.play_title != None: print("play_title:", zipp.play_title)
        if zipp.play_token != None: print("play_token:", zipp.play_token)
        if zipp.play_type != None: print("play_type:", zipp.play_type)

    elif user_choice == "channel":
        print("Content of channel:", zipp._channel_json)

    elif user_choice == "timer_cancel": zipp.timer_cancel()
    elif user_choice == "timer":
        print("Configured timer:", zipp.timer)
        zipp.timer_set(input("Input timer in seconds:"))

    elif user_choice == "info":
        if zipp.state   != None: print("State:", zipp.state)
        if zipp.name != None: print("Name:", zipp.name)
        if zipp.version != None: print("Version:", zipp.version)
        if zipp.volume  != None: print("Volume:", zipp.volume)
        if zipp.serialnumber != None: print("SerialNumber:", zipp.serialnumber)
        if zipp.devicecolor != None: print("DeviceColor:", zipp.devicecolor)
        if zipp.voicing != None: print("Voicing:", zipp.voicing)
        if zipp.room != None: print("Room:", zipp.room)
        if zipp.chargingstatus  != None: print("Charging status:", zipp.chargingstatus)
        if zipp.batterylevel  != None: print("BatteryLevel:", zipp.batterylevel)
        if zipp.timer  != None: print("Timer:", zipp.timer)
        if zipp.signalstrenght != None: print("SignalStrength:", zipp.signalstrenght)
        if zipp.mutestatus != None: print("MuteStatus:", zipp.mutestatus)
        
    elif user_choice == "exit":
        break
        
zipp.exit()
