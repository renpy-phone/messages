"""renpy
init -940 python in phone:
"""

# Public functions for game scripts, e.g. `$ phone.open("messages")`.

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


def open(app_id=None, screen=None, **kwargs):
    """Shows the phone and waits until the player closes it.

    `$ phone.open("messages", "phone_messages_thread", thread="alice")`
    """
    global _called
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


def clock_text():
    if state.clock is not None:
        return state.clock
    return _time.strftime(cfg.clock_format)


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
