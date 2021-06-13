# Libratone Zipp controller library in Python

This aims to control a Libratone Zipp speaker with a Python library, potentially usable in [Home Assistant](https://www.home-assistant.io/) with [this module](https://github.com/Chouffy/home_assistant_libratone_zipp).

Install it with `pip install python-libratone-zipp` - [pip page](https://pypi.org/project/python-libratone-zipp/)

## Usage

See example in `CLI.py`

## Roadmap

Nothing is guaranteed here!

### Module improvement

* [x] Clean text variables, declare variable on top instead of using text like "play"
* [x] Create a client
* [ ] Handle exit properly - currently threads can be locking
* [ ] Use discovery method instead of fixed IP

### Functionality coverage

* v1.0
    * [x] Set basic playback status: play, pause, stop, next, prev
    * [x] Play a Favorite
    * [x] Calculate state - But this is not use in HA
    * [x] Make it work with Home Assistant
    * [x] Publish on PyPi
* v1.1
    * [x] Set a Voicing
* v2.0
    * [x] Retrieve basic playback status: play, pause, stop, next, prev
    * [x] Set volume
    * [x] Retrieve volume
    * [x] Set to immediate standby
    * [x] Retrieve and set Voicing
    * [x] Retrieve current firmware, IP, serial number
    * [x] Retrieve actual speaker state (approximately)
* v3.0
    * [ ] Make the module async

Other functionalities:

* Current Playback info
    * [ ] Retrieve current playback source
    * [ ] Retrieve current title
    * [ ] Retrieve media type: bluetooth, spotify, aux, radio, ...
* Standby
    * [ ] Set a standby timer
    * [ ] Retrieve a standby timer
* Voicing & Room Setting
    * [ ] Set Room Setting
    * [ ] Retrieve current Room Setting
* Favorites
    * [ ] Set a Favorite
* Extended current playback info
    * [ ] Set extended playback status: shuffle, repeat
    * [ ] Retrieve extended playback status: shuffle, repeat
    * [ ] Set Source
    * [ ] Retrieve current source
* Speaker configuration
    * [ ] Retrieve speaker name
    * [ ] Retrieve speaker color
    * [ ] Set speaker name
    * [ ] Set speaker color
    * [ ] Retrieve current IP, serial number
    * [ ] Retrieve current battery and AC information
* Network
    * [ ] Retrieve current wifi information
    * [ ] Set wifi information
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
