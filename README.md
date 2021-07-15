# Libratone Zipp controller library in Python

This aims to control **one** Libratone Zipp speaker with a Python library, potentially usable in [Home Assistant](https://www.home-assistant.io/) with [this module](https://github.com/Chouffy/home_assistant_libratone_zipp).

Install it with `pip install python-libratone-zipp` - [pip page](https://pypi.org/project/python-libratone-zipp/)

Tested with Libratone Zipp 1, firmware 809.

## Usage

See example in `CLI.py`. You have to be able to listen to `3333/udp` and `7778/udp`!

Other files:

* `Test_SendCommandReceiveMessage.py` is used to shoot one command for tests purposes.
* `Test_LibratoneMessage.py` is to check LibratoneMessage class against a real message

## Functionality coverage

I'm currently happy with this coverage, so don't expect any updates other than maintenance.  
The only thing I'm very interested is defining Favorites!

* Module
    * [x] Clean text variables, declare variable on top instead of using text like "play"
    * [x] Create a Command Line Interface - CLI client
    * [x] Publish on PyPi
    * [x] Handle exit properly - but need max _KEEPALIVE_CHECK_PERIOD seconds to exit
    * [ ] Make the module usable with multiple speaker
    * [ ] Use discovery method instead of fixed IP
    * [ ] Make the module compatible with async from Home Assistant
* Playback status with Spotify & Radio
    * [x] Retrieve basic playback status: play, pause, stop
    * [x] Retrieve volume
    * [x] Retrieve current playback source
    * [x] Retrieve current title
    * [x] Retrieve mute status - but no logic implemented!
* Playback with Bluetooth or USB
    * [ ] Retrieve basic playback status: play, pause, stop
    * [ ] Retrieve media type: Bluetooth, aux, radio, ...
    * [ ] Retrieve extended playback status: shuffle, repeat
    * [ ] Set extended playback status: shuffle, repeat
* Playback control
    * [x] Set basic playback status: play, pause, stop, next, prev
    * [x] Set volume
* Standby
    * [x] Retrieve actual speaker state
    * [x] Calculate actual speaker state: UNKOWN, SLEEPING, ON, PLAYING, PAUSED, STOPPED
    * [x] Set to immediate standby and wakeup
    * [x] Set a standby timer
    * [x] Retrieve the defined duration of the standby timer
    * [ ] Calculate the actual standby timer
* Voicing & Room Setting
    * [x] Set a Voicing
    * [x] Retrieve active Voicing
    * [x] Retrieve all Voicing
    * [x] Set Room Setting
    * [x] Retrieve current Room Setting
    * [x] Retrieve all Room
* Favorites
    * [x] Play a Favorite
    * [x] List configured favorite but no processing (`_channel_json`)
    * [ ] Set a Favorite
* Extended current playback info
    * [ ] Set Source
    * [ ] Retrieve current source
* Speaker configuration
    * [x] Retrieve current firmware
    * [x] Retrieve speaker name
    * [x] Retrieve speaker color
    * [x] Set speaker name
    * [ ] Map out color codes + Set speaker color
    * [x] Retrieve current serial number
    * [x] Retrieve current battery level
    * [ ] Retrieve AC information
* Network
    * [ ] Retrieve current IP
    * [ ] Retrieve current Wi-Fi configuration
    * [x] Retrieve current Wi-Fi information
    * [ ] Set Wi-Fi configuration
* Multi-room
    * [ ] Implement SoundSpace Link

### Unimplemented commands

Following commands where identified but not implemented and/or implemented but not processed due to lack on `data` investigation. The list is not exhaustive!

From Android application, `com.libratone.model.LSSDPNode`:
command|function|notes
-|-|-
10  | fetchSourceInfo
103 | fetchDeviceState
152 | fetchSource
281 | fetchMusicServiceCapability | Answer a JSON
304 | fetchLimitedFunctionList | Answer 3 bytes
520 | fetchMuteStatus|Implemented but not processed
530 | fetchOtaAutoDownLoadStatus
537 | fetchWifiLinein
1284| fetchChargingStatus|Implemented but not processed
1285| fetchPrivateMode
1536| fetchUsbCurrentPlayId
1537| fetchUsbPlayMode
1538| fetchUsbSongInfo

## Acknowledgment

This work is based on the following:

* The Libratone command list is [coming from this work from Benjamin Hanke](https://www.loxwiki.eu/display/LOX/Libratone+Zipp+WLan+Lautsprecher)
* A lot of further work is based on APK decompilation
* Entity to use: [Media Player](https://developers.home-assistant.io/docs/core/entity/media-player)
* Example of [integrations](https://www.home-assistant.io/integrations/#media-player):
    * Simple: [Harman Kardon AVR integration](https://www.home-assistant.io/integrations/harman_kardon_avr/) which use [this module](https://github.com/Devqon/hkavr)
    * Simple: [Clementine Music Player integration](https://github.com/home-assistant/core/blob/dev/homeassistant/components/clementine/media_player.py)
    * Async: [Frontier Silicon integration](https://github.com/home-assistant/core/tree/dev/homeassistant/components/frontier_silicon) with [this module](https://github.com/zhelev/python-afsapi/tree/master/afsapi)
    * Async with extended features: [Yamaha integration](https://github.com/home-assistant/core/blob/dev/homeassistant/components/yamaha/) with [this module](https://github.com/wuub/rxv)
    * Async and simple: [anthemav integration](https://github.com/home-assistant/core/tree/dev/homeassistant/components/anthemav) with [this module](https://github.com/nugget/python-anthemav/tree/master/anthemav)

## License

See LICENSE file
