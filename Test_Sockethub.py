#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test the SocketHub with two Libratone speakers, emulating how Home Assistant
would interact with multiple devices in a single process.

Parameters (can be passed via arguments):
zipp1 = First Zipp speaker
zipp2 = Second Zipp speaker
"""

zipp1 = '192.168.xx.xx'
zipp2 = '192.168.xx.yy'

import sys
import time
import threading

# Try to import from installed package first, then from local repo
try:
    import python_libratone_zipp.LibratoneZipp as lz_mod
    from python_libratone_zipp import LibratoneZipp
except Exception:
    # Fallback: running from repo root where modules are in the same folder
    import LibratoneZipp as lz_mod  # type: ignore
    from LibratoneZipp import LibratoneZipp  # type: ignore

# Force the hub path (library will fallback if hub unavailable)
try:
    lz_mod.USE_SOCKET_HUB = True
except Exception:
    pass


def wait_for_attr(obj, attr, predicate, timeout=5.0, poll=0.1):
    deadline = time.time() + timeout
    last = getattr(obj, attr, None)
    while time.time() < deadline:
        last = getattr(obj, attr, None)
        try:
            if predicate(last):
                return last
        except Exception:
            pass
        time.sleep(poll)
    return last


def safe_int(x):
    try:
        return int(x)
    except Exception:
        return None


def device_summary(z):
    return f"name={getattr(z, 'name', None)} vol={getattr(z, 'volume', None)} ver={getattr(z, 'version', None)} state={getattr(z, 'state', None)}"


def ensure_bootstrap(z):
    # Ask a few basics, like HA would during entity setup
    z.name_get()
    z.version_get()
    z.volume_get()
    time.sleep(0.8)  # let replies arrive


def concurrent_call(funcs):
    threads = [threading.Thread(target=f, daemon=True) for f in funcs]
    for t in threads: t.start()
    for t in threads: t.join()


def choose_target_volume(current, base):
    """
    Picks a safe volume [0..100] that isn't equal to current.
    `base` is 11 or 22 so devices get distinct targets.
    """
    targets = [base, base+1, base+2, base+3]
    curr_i = safe_int(current)
    for v in targets:
        if 0 <= v <= 100 and v != curr_i:
            return v
    return (curr_i + 1) % 100 if curr_i is not None else base


def main():
    ip1 = sys.argv[1] if len(sys.argv) > 1 else zipp1
    ip2 = sys.argv[2] if len(sys.argv) > 2 else zipp2

    print(f"[SETUP] Initializing devices via hub: {ip1} and {ip2}")
    z1 = LibratoneZipp(ip1)
    z2 = LibratoneZipp(ip2)

    # like HA entity setup
    for z in (z1, z2):
        ensure_bootstrap(z)

    print("[INFO] After bootstrap:")
    print(f"  dev1({ip1}): {device_summary(z1)}")
    print(f"  dev2({ip2}): {device_summary(z2)}")

    # Remember original volumes to restore later
    orig_v1 = safe_int(getattr(z1, "volume", None))
    orig_v2 = safe_int(getattr(z2, "volume", None))

    # === Test 1: concurrent volume set ===
    tgt1 = choose_target_volume(orig_v1, base=11)
    tgt2 = choose_target_volume(orig_v2, base=22)
    print(f"[TEST1] Setting volumes concurrently: dev1->{tgt1}, dev2->{tgt2}")
    concurrent_call([
        lambda: z1.volume_set(tgt1),
        lambda: z2.volume_set(tgt2),
    ])
    # ask both to report back (like HA polling)
    concurrent_call([z1.volume_get, z2.volume_get])

    v1 = wait_for_attr(z1, "volume", lambda v: safe_int(v) == tgt1, timeout=6.0)
    v2 = wait_for_attr(z2, "volume", lambda v: safe_int(v) == tgt2, timeout=6.0)
    ok1 = safe_int(v1) == tgt1
    ok2 = safe_int(v2) == tgt2
    print(f"[RESULT1] dev1 volume={v1} ok={ok1}; dev2 volume={v2} ok={ok2}")

    # === Test 2: interleaved queries (like two HA entities polling) ===
    print("[TEST2] Interleaved name/version/volume_get on both devices")
    concurrent_call([
        lambda: (z1.name_get(), z1.version_get(), z1.volume_get()),
        lambda: (z2.name_get(), z2.version_get(), z2.volume_get()),
    ])
    time.sleep(0.6)
    print(f"[RESULT2] dev1: {device_summary(z1)}")
    print(f"[RESULT2] dev2: {device_summary(z2)}")

    # === Test 3: another concurrent set to fresh targets ===
    tgt1b = choose_target_volume(getattr(z1, "volume", None), base=13)
    tgt2b = choose_target_volume(getattr(z2, "volume", None), base=26)
    print(f"[TEST3] Another concurrent set: dev1->{tgt1b}, dev2->{tgt2b}")
    concurrent_call([
        lambda: z1.volume_set(tgt1b),
        lambda: z2.volume_set(tgt2b),
    ])
    concurrent_call([z1.volume_get, z2.volume_get])

    v1b = wait_for_attr(z1, "volume", lambda v: safe_int(v) == tgt1b, timeout=6.0)
    v2b = wait_for_attr(z2, "volume", lambda v: safe_int(v) == tgt2b, timeout=6.0)
    ok1b = safe_int(v1b) == tgt1b
    ok2b = safe_int(v2b) == tgt2b
    print(f"[RESULT3] dev1 volume={v1b} ok={ok1b}; dev2 volume={v2b} ok={ok2b}")

    # Summary
    passed = all([ok1, ok2, ok1b, ok2b])
    print("\n[SUMMARY]")
    if passed:
        print("✅ SocketHub multi-device send/receive looks good.")
    else:
        print("❌ Some checks failed. See results above.")
        sys.exit(2)

    # Restore original volumes (best effort)
    print("[CLEANUP] Restoring original volumes.")
    if orig_v1 is not None:
        z1.volume_set(orig_v1); z1.volume_get()
        wait_for_attr(z1, "volume", lambda v: safe_int(v) == orig_v1, timeout=4.0)
    if orig_v2 is not None:
        z2.volume_set(orig_v2); z2.volume_get()
        wait_for_attr(z2, "volume", lambda v: safe_int(v) == orig_v2, timeout=4.0)

    print("[CLEANUP] Exiting devices.")
    z1.exit()
    z2.exit()
    print("[DONE]")

if __name__ == "__main__":
    main()

