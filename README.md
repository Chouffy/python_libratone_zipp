# Libratone Zipp controller library in Python

This aims to control a Libratone Zipp speaker with a Python library usable in Home Assistant.

Install it with `pip install python-libratone-zipp` and use it with `from python_libratone_zipp import LibratoneZipp`! 

## Acknowledgment

This work is based on the following:

* The Libratone command list is [coming from this work from Benjamin Hanke](https://www.loxwiki.eu/display/LOX/Libratone+Zipp+WLan+Lautsprecher)
* I follow the general structure of [this HkAVR integration](https://github.com/Devqon/hkavr) and this [Clementine integration](https://github.com/jjmontesl/python-clementine-remote/tree/master/clementineremote)
* Also the [media_player entity](https://developers.home-assistant.io/docs/core/entity/media-player)

## Roadmap

* v1.0
    * [x] Set basic playback status: play, pause, stop, next, prev
    * [x] Set a Favorite
    * [x] Calculate state - But this is not use in HA
    * [x] Make it work with Home Assistant
    * [x] Publish on PyPi
* v2.0
    * [ ] Retrieve basic playback status: play, pause, stop, next, prev
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
    * [ ] Set a Voicing
    * [ ] Retrieve current Voicing
    * [ ] Set Room Setting
    * [ ] Retrieve current Room Setting
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
    * [ ] Set a Favorite
* Network
    * [ ] Retrieve current wifi information
    * [ ] Set wifi information
* Module things
    * [ ] Create a client
    * [ ] Use discovery method instead of fixed IP

## License

See LICENSE file
