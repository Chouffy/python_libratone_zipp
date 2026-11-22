# Changelog

## 5.0.0

Breaking: new asyncio API, the threaded `LibratoneZipp` class is gone.

* `LibratoneHub` (shared UDP sockets, polling, routing) and `LibratoneSpeaker` (state + commands)
* Speakers identified by serial number; followed across DHCP IP changes (unknown-IP re-identification, subnet sweep)
* Availability from the last reply; parse errors never stop the receive path
* Group state, master/slave, stereo channel and the real playing flag from the LSSDP status (UDP 1800)
* Source detection (Spotify, radio favorite, Bluetooth, DLNA), Bluetooth playback shown as playing
* New: audio channel (stereo/left/right), save favorite, rename, color get/set, sleep timer countdown,
  Wi-Fi network/signal, MAC, app-style link ids
* Favorite-started callback (heart button / app / us), `add_favorite_listener`
* Mute state: the touch-panel mute ("private mode", cmd 1285), read-only, pushed by the speaker and polled
* Packaging: `pyproject.toml`, `py.typed`, Python >= 3.12

## 4.1.0 and earlier

See the git history.
