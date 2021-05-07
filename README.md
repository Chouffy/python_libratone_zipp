# Libratone Zipp controller library in Python

This aims to control a Libratone Zipp speaker with a Python library, potentially usable in [Home Assistant](https://www.home-assistant.io/) with [this module](https://github.com/Chouffy/home_assistant_libratone_zipp).

Install it with `pip install python-libratone-zipp` - [pip page](https://pypi.org/project/python-libratone-zipp/)

## Usage

Functions return `True` if they are successful

Command | Action
-|-
**Initialization**
`from python_libratone_zipp import LibratoneZipp` | Import the library
`zipp = LibratoneZipp('192.168.1.99', "Zipp")` | Instanciate the LibratoneZipp class
**Properties**
`zipp.name` | Name of the speaker
`zipp.host` | IP adress of the speaker
**Playback commands**
`zipp.state`| State of the speaker - see below
`zipp.play()` | Play command
`zipp.pause()` | Pause command
`zipp.stop()` | Stop command
`zipp.next()` | Next track command
`zipp.prev()` | Previous track command
**Voicing (sound mode) commands**
`zipp.voicing` | Current voicing
`zipp.voicing_list` | List of all `<voicing_id>`
`zipp.voicing_set(<voicing_id>)` | Set the speaker to `<voicing_id>`

### States

Right now, state are calculated and not fetched from the device. Some of them (sleep) are not even used.

State variable | Variable content | Description
-|-|-
`STATE_OFF` | `"OFF"` | The speaker is off or cannot be reached
`STATE_SLEEP` | `"SLEEP"` | The speaker is in sleep mode (nightingale is off)
`STATE_IDLE` | `"IDLE"` | The speaker is active but don't play anything
`STATE_PLAY` | `"PLAY"` | The speaker is playing
`STATE_PAUSE` | `"PAUSE"` | The speaker is on pause - Not sure if it's a "true" state

## Roadmap

### Module improvement

* [ ] Clean text variables, declare variable on top instead of using text like "play"
* [ ] Create a client
* [ ] Use discovery method instead of fixed IP

### Functionnality coverage

* v1.0
    * [x] Set basic playback status: play, pause, stop, next, prev
    * [x] Set a Favorite
    * [x] Calculate state - But this is not use in HA
    * [x] Make it work with Home Assistant
    * [x] Publish on PyPi
* v1.1
    * [x] Set a Voicing
* v2.0
    * [ ] Retrieve basic playback status: play, pause, stop, next, prev
    * [ ] Set volume
* v3.0
    * [ ] Make the module async

Other functionalities:

* Volume
    * [ ] Set volume
    * [ ] Retrieve volume
* Current Playback info
    * [ ] Retrieve current playback source
    * [ ] Retrieve current title
    * [ ] Retrieve media type: bluetooth, spotify, aux, radio, ...
* Standby
    * [ ] Set to immediate standby
    * [ ] Set a standby timer
    * [ ] Retrive a standby timer
* Voicing & Room Setting
    * [ ] Retrieve current Voicing
    * [ ] Set Room Setting
    * [ ] Retrieve current Room Setting
* Favorites
    * [ ] Play a favorite
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
    * [ ] Retrieve current firmware, IP, serial number
    * [ ] Retrieve current battery and AC information
* Network
    * [ ] Retrieve current wifi information
    * [ ] Set wifi information
* Multi-room
    * [ ] Implement SoundSpace Link

## Acknowledgment

This work is based on the following:

* The Libratone command list is [coming from this work from Benjamin Hanke](https://www.loxwiki.eu/display/LOX/Libratone+Zipp+WLan+Lautsprecher)
* Entity to use: [Media Player](https://developers.home-assistant.io/docs/core/entity/media-player)
* Example of [integrations](https://www.home-assistant.io/integrations/#media-player):
    * Simple: [Harman Kardon AVR integration](https://www.home-assistant.io/integrations/harman_kardon_avr/) which use [this module](https://github.com/Devqon/hkavr)
    * Simple: [Clementine Music Player integration](https://github.com/home-assistant/core/blob/dev/homeassistant/components/clementine/media_player.py) which use [this module]()
    * Async: [Frontier Silicon integration](https://github.com/home-assistant/core/tree/dev/homeassistant/components/frontier_silicon) with [this module](https://github.com/zhelev/python-afsapi/tree/master/afsapi)
    * Async with extended features: [Yamaha integration](https://github.com/home-assistant/core/blob/dev/homeassistant/components/yamaha/) with [this module](https://github.com/wuub/rxv)

## License

See LICENSE file
