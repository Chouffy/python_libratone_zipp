#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Command-Line Interface for the `python_libratone_zipp` module.
"""

from python_libratone_zipp import LibratoneZipp

zipp = LibratoneZipp('192.168.1.31')

zipp.get_all()

while True:
    user_choice = input("Input your command: play, pause, stop, next, prev, play_favorite, voicing, volume, info, exit? ")

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

    elif user_choice == "play_favorite":
        user_choice = input("Input favorite ID: 1, 2, ... 5? ")
        zipp.favorite_play(user_choice)

    elif user_choice == "voicing":
        user_choice = input("Input voicing ID: neutral, easy, ...? ")
        zipp.voicing_set(user_choice)

    elif user_choice == "volume":
        user_choice = input("Input volume 0...100? ")
        zipp.volume_set(user_choice)

    elif user_choice == "info":
        if zipp.voicing != None: print("Voicing: " + zipp.voicing)
        if zipp.state   != None: print("State: " + zipp.state)
        if zipp.volume  != None: print("Volume: " + zipp.volume)
        
    elif user_choice == "exit":
        break
        
zipp.exit()