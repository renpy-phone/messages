"""renpy
init -940 python in phone:
"""

# Public functions for game scripts, e.g. `$ phone.open("messages")`.

import re as _re
import time as _time


def show(app_id=None, screen=None, **kwargs):
    """Shows the phone and lets the script carry on (non-blocking).

    With no app the phone opens on the home screen.
    """
    if app_id is None:
        state.home()
    else:
        state.launch(app_id, screen, **kwargs)
    renpy.show_screen("phone", _layer=cfg.layer, _zorder=cfg.zorder)
    mutated()


_open_next = None  # (app_id, screen, kwargs) for the next phone.open()


def open_next(app_id=None, screen=None, **kwargs):
    """Makes the next phone.open() show this app and screen instead of the
    ones it is given. Used when the statement that opened the phone runs
    again, e.g. after a phone call made from it.
    """
    global _open_next
    _open_next = (app_id, screen, dict(kwargs))


def open(app_id=None, screen=None, **kwargs):
    """Shows the phone and waits until the player closes it.

    `$ phone.open("messages", "phone_messages_thread", thread="alice")`
    """
    global _called, _open_next
    if _open_next is not None:
        app_id, screen, kwargs = _open_next
        _open_next = None
    if app_id is None:
        state.home()
    else:
        state.launch(app_id, screen, **kwargs)
    _called = True
    try:
        renpy.call_screen("phone", _layer=cfg.layer, _zorder=cfg.zorder)
    finally:
        _called = False


def close():
    """Closes the phone. From a screen, prefer the phone.Close() action.

    If the phone was opened with phone.open(), this also ends the wait; the
    return value then has to reach Ren'Py, e.g. via Function(phone.close).
    """
    if _called:
        return Close()()
    renpy.hide_screen("phone", layer=cfg.layer)
    mutated()


def is_open():
    return renpy.get_screen("phone", layer=cfg.layer) is not None


def is_showing(screen):
    """True when the phone is open on `screen` (e.g. a conversation)."""
    return is_open() and state.current()[0] == screen


def enable():
    state.enabled = True


def disable():
    """Stops the player from opening the phone (hides the HUD button too)."""
    state.enabled = False


def show_hud():
    state.hud_visible = True


def hide_hud():
    state.hud_visible = False


def set_time(text):
    """Sets the status bar clock, e.g. "21:34". None shows the real time."""
    state.clock = text


def set_battery(percent):
    state.battery = max(0, min(100, int(percent)))


def clock_24h():
    """True for a 24-hour clock: the player's setting, else cfg.clock_format."""
    pref = store.persistent._phone_clock_24h
    if pref is None:
        return "%H" in cfg.clock_format
    return bool(pref)


def clock_text():
    pref = store.persistent._phone_clock_24h
    if pref is None:
        return state.clock if state.clock is not None else _time.strftime(cfg.clock_format)

    # The player picked 12 or 24 hours: reformat real and story ("21:34") times.
    if state.clock is None:
        now = _time.localtime()
        hour, minute = now.tm_hour, now.tm_min
    else:
        m = _re.match(r"\s*(\d{1,2}):(\d\d)\s*([AaPp][Mm])?\s*$", state.clock)
        if m is None or int(m.group(1)) > 23:
            return state.clock
        hour, minute = int(m.group(1)), int(m.group(2))
        if m.group(3):
            hour = hour % 12 + (12 if m.group(3).lower() == "pm" else 0)
    if pref:
        return "{:02d}:{:02d}".format(hour, minute)
    return "{}:{:02d} {}".format((hour + 11) % 12 + 1, minute, "AM" if hour < 12 else "PM")


def install_app(app_id):
    state.installed[app_id] = True


def uninstall_app(app_id):
    state.installed[app_id] = False


# Contacts ------------------------------------------------------------------

def add_contact(who):
    """Puts a contact in the address book."""
    state.set_contact_data(who, "known", True)


def remove_contact(who):
    state.set_contact_data(who, "known", False)


def rename_contact(who, name):
    """Changes a contact's display name for this playthrough."""
    state.set_contact_data(who, "name", name)


def set_avatar(who, avatar):
    state.set_contact_data(who, "avatar", avatar)


def set_call_label(who, label):
    """Changes the label called when the player phones `who` (None: no answer)."""
    state.set_contact_data(who, "call_label", label)


def known_contacts():
    return [c for c in contacts.values() if c.known]


# Sounds and notifications --------------------------------------------------

def play_sound(event):
    """Plays cfg.sounds[event] if the player has phone sounds enabled."""
    fn = cfg.sounds.get(event)
    if fn and store.persistent._phone_sounds is not False:
        renpy.play(fn, channel=cfg.channel)


def notify(title, text="", app_id=None, icon=None, sound="notification"):
    """Shows a banner at the top of the screen while the phone is closed.

    Apps call this when something arrives; games can call it too.
    """
    if sound:
        play_sound(sound)
    if is_open() or not cfg.notifications or store.persistent._phone_notifications is False:
        return
    if not renpy.has_screen("phone_notification"):
        return
    renpy.show_screen(
        "phone_notification", title=title, text=text, app_id=app_id, icon=icon,
        _layer=cfg.layer, _zorder=cfg.zorder + 1,
    )


def hud_visible():
    s = globals().get("state")
    return bool(cfg.hud and s is not None and s.hud_visible and s.enabled and not is_open())


def reset_apps():
    """Resets every app's saved state to its starting value (for tests)."""
    for app in apps.values():
        reset = getattr(app, "reset", None)
        if reset is not None:
            reset()


# Player preferences (shared by all saves) ----------------------------------

def set_theme(name):
    """Switches the phone theme ("light", "dark" or any key of cfg.themes)."""
    if name not in cfg.themes:
        raise Exception("phone.set_theme: unknown theme {!r}.".format(name))
    store.persistent._phone_theme = name
    store.gui.rebuild()


def set_text_scale(scale):
    """Scales phone text, e.g. 0.85, 1.0 or 1.2."""
    store.persistent._phone_text_scale = scale
    store.gui.rebuild()


# The player -----------------------------------------------------------------

def player_name():
    """The player's display name: set_player_name() or cfg.player_name."""
    name = getattr(state, "player_name", None) if globals().get("state") is not None else None
    return renpy.substitute(name if name is not None else cfg.player_name)


def player_handle():
    handle = getattr(state, "player_handle", None) if globals().get("state") is not None else None
    return renpy.substitute(handle if handle is not None else cfg.player_handle)


def set_player_name(name, handle=None):
    """Sets the player's name (and optionally social handle) for this
    playthrough, e.g. after the player types it in. "[var]" works too.
    """
    state.player_name = name
    if handle is not None:
        state.player_handle = handle
