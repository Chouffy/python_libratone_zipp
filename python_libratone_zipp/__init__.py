"""Control Libratone Zipp (and compatible) WiFi speakers over the local network (asyncio).

    import asyncio
    from python_libratone_zipp import LibratoneHub

    async def main():
        hub = LibratoneHub()
        await hub.start()                       # binds UDP 7778 and 3333 (the speakers reply to fixed ports)
        speaker = hub.add_speaker("192.168.1.20", serial=None, name="Kitchen")
        speaker.add_listener(lambda: print(speaker.name, speaker.play_status, speaker.volume))
        await asyncio.sleep(5)
        speaker.set_volume(20)
        await hub.stop()

    asyncio.run(main())
"""
from .hub import LibratoneHub
from .protocol import Cmd
from .speaker import LibratoneSpeaker

__version__ = "5.0.0"
__all__ = ["Cmd", "LibratoneHub", "LibratoneSpeaker", "__version__"]
