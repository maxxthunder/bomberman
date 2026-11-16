"""EmuHawk's --lua opens the Lua Console as a window of its own, which a minimized start doesn't cover.
start() watches for it in the background and hides it. Windows only; one EmuHawk runs at a time."""
import ctypes, threading, time


def _watch(seconds):
    u = ctypes.windll.user32
    def cb(h, _):
        t = ctypes.create_unicode_buffer(64); u.GetWindowTextW(ctypes.c_void_p(h), t, 64)
        if t.value == "Lua Console" and u.IsWindowVisible(ctypes.c_void_p(h)): u.ShowWindow(ctypes.c_void_p(h), 0)
        return True
    cb = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)(cb)
    for _ in range(seconds * 20):
        u.EnumWindows(cb, 0); time.sleep(0.05)


def start(seconds=60):
    threading.Thread(target=_watch, args=(seconds,), daemon=True).start()
