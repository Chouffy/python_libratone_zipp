#!/usr/bin/env python3
"""Command line client for python_libratone_zipp.

    python CLI.py 192.168.1.20 status
    python CLI.py 192.168.1.20 watch                 # print every change until Ctrl+C
    python CLI.py 192.168.1.20 play|pause|stop|next|prev
    python CLI.py 192.168.1.20 volume 25
    python CLI.py 192.168.1.20 favorite 3
    python CLI.py 192.168.1.20 sleep|wake
    python CLI.py 192.168.1.20 channel stereo|left|right

Needs UDP 7778 and 3333 free on this machine (the speakers always answer to these ports).
"""
from __future__ import annotations

import argparse
import asyncio

from python_libratone_zipp import LibratoneHub, LibratoneSpeaker


def describe(spk: LibratoneSpeaker) -> str:
    group = f"{spk.group_role} of {spk.group_link_id}" if spk.group_link_id else "not linked"
    return (
        f"{spk.name} ({spk.serial}, firmware {spk.version}) at {spk.host}\n"
        f"  state:   {'sleeping' if spk.is_sleeping else spk.effective_status}   source: {spk.source}\n"
        f"  media:   {spk.media_title} - {spk.media_artist}\n"
        f"  volume:  {spk.volume}   voicing: {spk.voicing}   room: {spk.room}   channel: {spk.channel}\n"
        f"  group:   {group}\n"
        f"  battery: {spk.battery}%   wifi: {spk.ssid} ({spk.wifi_bars}/5)   color: {spk.color}\n"
        f"  favorites: {', '.join(spk.favorite_names)}"
    )


async def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("host")
    ap.add_argument("command", nargs="?", default="status")
    ap.add_argument("value", nargs="?")
    a = ap.parse_args()

    hub = LibratoneHub()
    await hub.start()
    spk = hub.add_speaker(a.host, serial=None, name=None)
    try:
        if not await hub.probe(a.host, timeout=3):
            raise SystemExit(f"{a.host} does not answer")
        await asyncio.sleep(2)  # let the first full refresh arrive
        cmd = a.command
        if cmd == "status":
            print(describe(spk))
        elif cmd == "watch":
            spk.add_listener(lambda: print("---\n" + describe(spk)))
            print(describe(spk))
            await asyncio.Event().wait()
        elif cmd in ("play", "pause", "stop", "next", "prev"):
            spk.play_control(cmd)
        elif cmd == "volume":
            spk.set_volume(int(a.value))
        elif cmd == "favorite":
            spk.play_favorite(a.value)
        elif cmd == "sleep":
            spk.sleep()
        elif cmd == "wake":
            spk.wake()
        elif cmd == "channel":
            spk.set_channel(a.value)
        else:
            raise SystemExit(f"unknown command {cmd}")
        if cmd not in ("status", "watch"):
            await asyncio.sleep(2)
            print(describe(spk))
    finally:
        await hub.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
