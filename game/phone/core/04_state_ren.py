"""renpy
init -960 python in phone:
"""

# Saved, per-playthrough state shared by the whole phone.


class PhoneState(object):
    def __init__(self):
        self.version = 1
        self.uid = 0

        # Navigation: a stack of [screen, kwargs] for the open app. An empty
        # stack means the home screen. kwargs must be picklable (use ids).
        self.app = None
        self.nav = []

        self.enabled = True  # False blocks opening the phone
        self.hud_visible = True
        self.installed = {}  # app id -> bool, overrides App.installed
        self.contact_data = {}  # contact id -> {"known", "name", "avatar", "call_label"}

        self.clock = None  # status bar text, None for the real time
        self.battery = 100
        self.wallpaper = None  # wallpaper id, None for cfg.default_wallpaper
        self.player_name = None  # None: cfg.player_name
        self.player_handle = None  # None: cfg.player_handle

    def next_uid(self):
        self.uid += 1
        return self.uid

    # Navigation ------------------------------------------------------------

    def current(self):
        """(screen, kwargs) to display, or (None, {}) for the home screen."""
        if not self.nav:
            return None, {}
        screen, kwargs = self.nav[-1]
        return screen, kwargs

    def launch(self, app_id, screen=None, **kwargs):
        app = apps.get(app_id)
        if app is None:
            raise Exception("phone: unknown app {!r}.".format(app_id))
        self.app = app_id
        self.nav = [[app.screen, {}]]
        if screen is not None and screen != app.screen:
            self.nav.append([screen, dict(kwargs)])
        elif kwargs:
            self.nav[0][1] = dict(kwargs)
        app.on_launch(**kwargs)

    def navigate(self, screen, **kwargs):
        self.nav.append([screen, dict(kwargs)])

    def replace(self, screen, **kwargs):
        if self.nav:
            self.nav.pop()
        self.nav.append([screen, dict(kwargs)])

    def back(self):
        if self.nav:
            self.nav.pop()
        if not self.nav:
            self.app = None

    def home(self):
        self.nav = []
        self.app = None

    # Contacts --------------------------------------------------------------

    def set_contact_data(self, contact, key, value):
        cid = contact_id(contact)
        data = dict(self.contact_data.get(cid, {}))
        data[key] = value
        self.contact_data[cid] = data


def _core_after_load():
    """Brings saves from older framework versions up to date."""
    s = globals().get("state")
    if s is None:
        return
    # Version 1 is the first release; migrations go here, e.g.
    # if s.version < 2: ...; s.version = 2
    for k, v in PhoneState().__dict__.items():
        if not hasattr(s, k):
            setattr(s, k, v)


if _core_after_load not in store.config.after_load_callbacks:
    store.config.after_load_callbacks.append(_core_after_load)


"""renpy
default phone.state = phone.PhoneState()
"""
