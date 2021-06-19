#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Command-Line Interface for the `python_libratone_zipp` module.
"""

from python_libratone_zipp import LibratoneZipp

zipp = LibratoneZipp(host='192.168.1.31')

while True:
    user_choice = input("Input your command: play, pause, stop, next, prev, sleep, wakeup, fav_play, voicing, room, volume, name_set, info, exit? ")

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

    elif user_choice == "info":
        if zipp.version != None: print("Version:", zipp.version)
        if zipp.name != None: print("Name:", zipp.name)
        if zipp.voicing != None: print("Voicing:", zipp.voicing)
        if zipp.room != None: print("Room:", zipp.room)
        if zipp.state   != None: print("State:", zipp.state)
        if zipp.volume  != None: print("Volume:", zipp.volume)
        if zipp.chargingstatus  != None: print("Charging status:", zipp.chargingstatus)
        if zipp.powermode  != None: print("Power mode:", zipp.powermode)
        
    elif user_choice == "exit":
        break
        
zipp.exit()
