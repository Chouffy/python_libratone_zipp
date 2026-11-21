# Libratone Zipp controller library in Python

Control one or multiple Libratone Zipp speakers over the local network with an **asyncio** Python library,
used by the [Home Assistant integration](https://github.com/Chouffy/home_assistant_libratone_zipp).

Install it with `pip install python-libratone-zipp` - [pip page](https://pypi.org/project/python-libratone-zipp/)

Tested with Libratone Zipp (LTH300), firmware 809, 879. The first-generation Zipp Mini works the same way.

## Version 5 (asyncio) - breaking changes

Version 5 replaces the threaded `LibratoneZipp` class with an asyncio API and no longer needs fixed IPs:

* `LibratoneHub` owns the UDP sockets (the speakers always answer to ports `7778` and `3333`, so one hub per
  machine), polls the speakers and routes replies.
* `LibratoneSpeaker` holds the state of one speaker and sends commands. Speakers are identified by **serial
  number**: when a speaker gets a new IP from DHCP, the hub finds it again (unknown IP reporting a known serial,
  or a small subnet sweep while a speaker is missing).
* Group (SoundSpace Link) state, stereo channel and the real "playing" flag come from the speaker's LSSDP status
  (UDP 1800), so they are known right after start-up.

Code using the 4.x API needs to be ported; see `CLI.py` for a complete example.

## Usage

```python
import asyncio
from python_libratone_zipp import LibratoneHub

async def main():
    hub = LibratoneHub()
    await hub.start()                                   # needs UDP 7778 and 3333 free
    speaker = hub.add_speaker("192.168.1.20", serial=None, name="Kitchen")
    speaker.add_listener(lambda: print(speaker.name, speaker.effective_status, speaker.media_title))
    await asyncio.sleep(5)                              # first refresh
    speaker.set_volume(20)
    speaker.play_favorite(3)
    await hub.stop()

asyncio.run(main())
```

Command line: `python CLI.py <ip> status|watch|play|pause|stop|next|prev|volume N|favorite N|sleep|wake|channel stereo|left|right`

Notes:

* Don't flood a speaker: sending GETs at ~25/s for minutes hung a speaker's control service until its battery ran
  flat. The hub polls a handful of values every 10 s.
* `SET 150` is the factory reset. The library never sends it.

## Functionality coverage

* Module
    * [x] Clean text variables, declare variable on top instead of using text like "play"
    * [x] Create a Command Line Interface - CLI client
    * [x] Publish on PyPi
    * [x] Make the module usable with multiple speaker
    * [x] Use discovery method instead of fixed IP (speakers tracked by serial, re-found after IP changes)
    * [x] Make the module compatible with async from Home Assistant
* Playback status with Spotify & Radio
    * [x] Retrieve basic playback status: play, pause, stop
    * [x] Retrieve volume
    * [x] Retrieve current playback source (Spotify, radio favorite, Bluetooth, DLNA)
    * [x] Retrieve current title, artist, album, playlist, cover
    * [x] Retrieve mute status (read-only: the speaker mutes itself when its touch panel is held)
* Playback with Bluetooth or USB
    * [x] Retrieve basic playback status: playing / paused (LSSDP; cmd 51 reports Bluetooth as paused)
    * [x] Retrieve media type: Bluetooth, radio, streaming, DLNA (aux untested)
    * [ ] Retrieve extended playback status: shuffle, repeat (not exposed by the speaker)
    * [ ] Set extended playback status: shuffle, repeat
* Playback control
    * [x] Set basic playback status: play, pause, stop, next, prev
    * [x] Set volume
* Standby
    * [x] Retrieve actual speaker state
    * [x] Set to immediate standby and wakeup
    * [x] Set a standby timer
    * [x] Calculate the actual standby timer (GET 15 returns the remaining seconds)
* Voicing & Room Setting
    * [x] Set / retrieve Voicing, list all
    * [x] Set / retrieve Room Setting, list all
* Favorites
    * [x] Play a Favorite, list favorites by name
    * [x] Set a Favorite (radio station playing now; Spotify content not yet)
* Extended current playback info
    * [ ] Set Source (not possible over the network, except favorites)
    * [x] Retrieve current source
* Speaker configuration
    * [x] Retrieve current firmware
    * [x] Retrieve / set speaker name
    * [x] Retrieve / set speaker color (all 15 color codes mapped, see below)
    * [x] Retrieve current serial number
    * [x] Retrieve current battery level
    * [ ] Retrieve AC information
* Network
    * [x] Retrieve current IP, MAC (LSSDP)
    * [x] Retrieve current Wi-Fi network (539) and signal (529)
    * [ ] Set Wi-Fi configuration (possible through the speaker's web UI, `cgi?SetNet`)
* Multi-room
    * [x] Implement SoundSpace Link (join / leave)
    * [x] Retrieve group state and master at any time (LSSDP)
    * [x] Set the audio channel: stereo / left / right
* Firmware, setup, factory reset (open - contributions welcome)
    * [ ] Firmware update status (cmd 65 JSON notifications; the web UI `cgi?Update` also accepts local uploads)
    * [ ] Wi-Fi setup of a factory-new speaker without the app (setup hotspot + web UI `cgi?SetNet`)
    * [ ] Factory reset (`SET 150` is known; deliberately not implemented)

### Ports

Port | Direction | Use
-|-|-
7777/udp | to speaker | commands
7778/udp | to controller | replies (fixed port, whatever the source port), also LSSDP replies
3333/udp | to controller | notifications, acknowledged to the speaker's 3334/udp
1800/udp | both | LSSDP status: broadcast every ~10 s, answers a unicast M-SEARCH
49152/tcp | to speaker | UPnP/DLNA media renderer (`/description.xml`, AVTransport)
80/tcp | to speaker | web UI: `cgi?Overview`, `cgi?Network` (Wi-Fi setup), `cgi?Update` (firmware)
8038/tcp | to speaker | Spotify Connect (zeroconf, eSDK)

### Commands

`aaaa | type (1 get, 2 set) | cmd (2 bytes) | status | random id (2) | length (2) | data`, sent to UDP 7777.

Function names in the second column come from the decompiled Android app (`com.libratone.model.LSSDPNode`,
found by Chouffy and [Benjamin Hanke](https://www.loxwiki.eu/display/LOX/Libratone+Zipp+WLan+Lautsprecher)).
The notes, and the commands without an app name, come from packet captures and tests (2025-2026).

command|function|notes
-|-|-
5   | version |
10  | fetchSourceInfo | 7 bytes: [0] mode (0x34 streaming, 0x3f radio favorite, 0x41 local/Bluetooth, 0x3b group slave, 0x32 DLNA), [2] 0x08 = Bluetooth playing
14  | current power mode | 0 awake, 1 idle, 2 sleeping
15  | timer | SET `2<seconds>` start, `F0` cancel, `20` sleep now, `00` wake; GET `'2'` + remaining seconds (uint16 LE)
40  | play control | PLAY / PAUSE / STOP / NEXT / PREV
50  | source mode notification | byte 0 of cmd 10
51  | play status | 0 playing, 1 stopped, 2 paused
64  | volume | 0-100
65  | firmware update | JSON notifications
90  | name | GET / SET
103 | fetchDeviceState | notifications `FREE`, `GROUPED,LINK x`, `MASTER,LINK x`, `SLAVE,LINK x`; GET empty
150 | factory reset | SET, never sent by the library
152 | fetchSource | binary, not decoded
256/257 | battery |
275 / 276 / 277 | favorites list / save favorite / play favorite | JSON
278 | player | JSON with title, artist, album, cover, play_type
279 / 281 | capabilities / fetchMusicServiceCapability | JSON
304 | fetchLimitedFunctionList |
502 / 503 | group join / leave | `LINK <Name>_<Serial>-<Color>_<random>` to every member
504 / 505 | pair state / notification | `UNPAIRED`
512 | audio channel | SET 0 stereo / 1 left / 2 right; read via LSSDP
516 / 518, 517 / 519, 524 / 525 | voicing, room: get / set / list |
520 | fetchMuteStatus | `MUTE` / `UNMUTE`, read-only (touch panel held)
528 | ? | `300`
529 | signal strength | `-89,-34,5/5`
530 | fetchOtaAutoDownLoadStatus |
537 | fetchWifiLinein |
539 | Wi-Fi network |
769 | serial number |
770 / 771 | color get / set | 1001 Pepper Black, 1002 Salty Grey, 1003 Steel Blue, 1004 Raspberry Red, 1005 Almond Brown, 1006 Icy Blue (wool covers); 2001 Cloudy Grey, 2002 Graphite Grey, 2003 Victory Red, 2004 Deep Lagoon, 2005 Sangria, 2006 Atlantic Deep, 2007 Signal, 2008 Nude, 2009 Pastel Blue (mesh covers)
1284| fetchChargingStatus |
1285| fetchPrivateMode |
1536 - 1538 | fetchUsbCurrentPlayId / fetchUsbPlayMode / fetchUsbSongInfo |

Still unknown (the app queries them, replies are empty or a bare value; contributions welcome):
`260` (`0`), `288` (empty), `515` (`0`), `528` (`300`, auto-standby seconds?), `532` (`00 00`), `535` (`ff ff ff ff`),
`1286` (the app SETs `0` / `2`), `1541` (empty), and what `504` (`UNPAIRED`) is for.

LSSDP: a unicast `M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1800\r\nPROTOCOL:Version 1.0` to
`<speaker>:1800` is answered on UDP 7778 with `DeviceState: <role F/G/M/S>,<channel S/L/R>,<playing P/N>`,
`ZoneID: LINK <link id>`, `DeviceID` (MAC) and more. Note: a speaker whose control service hung still answered
LSSDP, so it is not a sign of life; the library uses command replies for availability.

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
