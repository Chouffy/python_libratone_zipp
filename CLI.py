#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Command-Line Interface for the `python_libratone_zipp` module.
"""

from python_libratone_zipp import LibratoneZipp

zipp = LibratoneZipp(host='192.168.1.31', localhost='192.168.1.10')

while True:
    user_choice = input("Input your command: play, pause, stop, next, prev, sleep, wakeup, fav_play, voicing, voicing_list, volume, info, exit? ")

    if user_choice == "play":
        zipp.play()
    elif user_choice == "pause":
        zipp.pause()
    elif user_choice == "stop":
        zipp.stop()
    elif user_choice == "next":
        zipp.next()
    elif user_choice == "prev":
        zipp.prev()
    elif user_choice == "sleep":
        zipp.sleep()
    elif user_choice == "wakeup":
        zipp.wakeup()

    elif user_choice == "fav_play":
        user_choice = input("Input favorite ID: 1, 2, ... 5? ")
        zipp.favorite_play(user_choice)

    elif user_choice == "voicing":
        user_choice = input("Input voicing ID: Neutral, Easy Listening, ...? ")
        zipp.voicing_set(user_choice)
    elif user_choice == "voicing_list":
        print(zipp.voicing_list())

    elif user_choice == "volume":
        user_choice = input("Input volume 0...100? ")
        zipp.volume_set(user_choice)

    elif user_choice == "info":
        if zipp.version != None: print("Version:", zipp.version)
        if zipp.voicing != None: print("Voicing:", zipp.voicing)
        if zipp.state   != None: print("State:", zipp.state)
        if zipp.volume  != None: print("Volume:", zipp.volume)
        if zipp.chargingstatus  != None: print("Charging status:", zipp.chargingstatus)
        if zipp.powermode  != None: print("Power mode:", zipp.powermode)
        
    elif user_choice == "exit":
        break
        
zipp.exit()