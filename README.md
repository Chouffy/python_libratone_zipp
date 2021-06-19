# Libratone Zipp controller library in Python

This aims to control a Libratone Zipp speaker with a Python library, potentially usable in [Home Assistant](https://www.home-assistant.io/) with [this module](https://github.com/Chouffy/home_assistant_libratone_zipp).

Install it with `pip install python-libratone-zipp` - [pip page](https://pypi.org/project/python-libratone-zipp/)

## Usage

See example in `CLI.py`.  
You have to be able to listen to `3333/udp` and `7778/udp`!

## Functionality coverage

* Module
    * [x] Clean text variables, declare variable on top instead of using text like "play"
    * [x] Create a Command Line Interface - CLI client
    * [x] Publish on PyPi
    * [ ] Handle exit properly - currently threads can be locking
    * [ ] Use discovery method instead of fixed IP
    * [ ] Make the module compatible with async from Home Assistant
* Playback status
    * [x] Retrieve basic playback status: play, pause, stop
    * [x] Retrieve actual speaker state (approximately) - sleep and awake
    * [x] Retrieve volume
    * [ ] Retrieve current playback source
    * [ ] Retrieve current title
    * [ ] Retrieve media type: bluetooth, spotify, aux, radio, ...
* Playback control
    * [x] Set basic playback status: play, pause, stop, next, prev
    * [x] Set volume
* Standby
    * [x] Set to immediate standby
    * [ ] Set a standby timer
    * [ ] Retrieve a standby timer
* Voicing & Room Setting
    * [x] Set a Voicing
    * [x] Retrieve active Voicing
    * [ ] Retrieve all Voicing
    * [ ] Set Room Setting
    * [ ] Retrieve current Room Setting
    * [x] Retrieve all Room
* Favorites
    * [x] Play a Favorite
    * [ ] Set a Favorite
* Extended current playback info
    * [ ] Set extended playback status: shuffle, repeat
    * [ ] Retrieve extended playback status: shuffle, repeat
    * [ ] Set Source
    * [ ] Retrieve current source
* Speaker configuration
    * [x] Retrieve current firmware
    * [x] Retrieve speaker name
    * [ ] Retrieve speaker color
    * [x] Set speaker name
    * [ ] Set speaker color
    * [ ] Retrieve current IP, serial number
    * [ ] Retrieve current battery and AC information
* Network
    * [ ] Retrieve current Wi-Fi information
    * [ ] Set Wi-Fi information
* Multi-room
    * [ ] Implement SoundSpace Link

## Acknowledgment

This work is based on the following:

* The Libratone command list is [coming from this work from Benjamin Hanke](https://www.loxwiki.eu/display/LOX/Libratone+Zipp+WLan+Lautsprecher)
* A lot of further work is based on APK decompilation
* Entity to use: [Media Player](https://developers.home-assistant.io/docs/core/entity/media-player)
* Example of [integrations](https://www.home-assistant.io/integrations/#media-player):
    * Simple: [Harman Kardon AVR integration](https://www.home-assistant.io/integrations/harman_kardon_avr/) which use [this module](https://github.com/Devqon/hkavr)
    * Simple: [Clementine Music Player integration](https://github.com/home-assistant/core/blob/dev/homeassistant/components/clementine/media_player.py) which use [this module]()
    * Async: [Frontier Silicon integration](https://github.com/home-assistant/core/tree/dev/homeassistant/components/frontier_silicon) with [this module](https://github.com/zhelev/python-afsapi/tree/master/afsapi)
    * Async with extended features: [Yamaha integration](https://github.com/home-assistant/core/blob/dev/homeassistant/components/yamaha/) with [this module](https://github.com/wuub/rxv)
    * Async and simple: [anthemav integration](https://github.com/home-assistant/core/tree/dev/homeassistant/components/anthemav) with [this module](https://github.com/nugget/python-anthemav/tree/master/anthemav)

## License

See LICENSE file
