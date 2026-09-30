"""renpy
init -970 python in phone:
"""

# Apps are static definitions registered at init time. Each app keeps its
# story state in its own `default phone.<something>` variable.

apps = {}  # id -> App


class App(python_object):
    """Base class for phone apps. Subclass it and call phone.register_app().

    `id`        unique string id.
    `name`      name under the home screen icon (wrap in _() to translate).
    `screen`    screen shown when the app is launched. It is `use`d inside the
                phone shell and receives the keyword arguments given to
                phone.Launch() / phone.Navigate().
    `icon`      displayable for the icon, or None to draw `glyph` on `color`.
    `order`     position on the home screen, lowest first.
    `installed` whether the app is on the home screen at the start of a game.
    """

    id = None
    name = ""
    screen = None
    icon = None
    glyph = "?"
    color = "#8e8e93"
    order = 100
    installed = True

    def __repr__(self):
        return "<phone app {}>".format(self.id)

    def badge(self):
        """Number shown on the icon, e.g. unread messages."""
        return 0

    def on_launch(self, **kwargs):
        """Called when the app is opened from the home screen or by script."""
        return

    def is_installed(self):
        s = globals().get("state")
        if s is None:
            return self.installed
        return s.installed.get(self.id, self.installed)


def register_app(app):
    """Adds an App instance to the phone. Call from an init python block."""
    init_only("phone.register_app()")
    if not app.id:
        raise Exception("phone.register_app: {!r} has no id.".format(app))
    old = apps.get(app.id)
    if old is not None and not isinstance(app, type(old)):
        # Replacing a built-in app is allowed with a subclass of it.
        raise Exception("phone.register_app: app id {!r} is already used by {!r}.".format(app.id, apps[app.id]))
    apps[app.id] = app
    return app


def get_app(app_id):
    return apps.get(app_id)


def home_apps():
    """Installed apps in home screen order."""
    rv = [a for a in apps.values() if a.is_installed()]
    if cfg.app_order:
        order = list(cfg.app_order)
        rv.sort(key=lambda a: (order.index(a.id) if a.id in order else len(order), a.order, a.id))
    else:
        rv.sort(key=lambda a: (a.order, a.id))
    return rv


def total_badges():
    return sum(a.badge() for a in home_apps())
