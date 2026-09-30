"""renpy
init -920 python in phone:
"""

# Settings app: the player's phone preferences. They are stored in
# `persistent`, so they are shared by every save:
#
#     persistent._phone_theme          theme name (phone.set_theme)
#     persistent._phone_text_scale     text size (phone.set_text_scale)
#     persistent._phone_notifications  False hides banners (None: on)
#     persistent._phone_sounds         False mutes phone sounds (None: on)
#     persistent._phone_clock_24h      True/False, None follows cfg.clock_format
#
# Games can add rows of their own with phone.add_toggle_setting() and
# phone.add_action_setting().

# Shown in the About section. Change them from an `init -2 python in phone:`
# block like the rest of cfg.
cfg.device_name = _("My Phone")
cfg.device_model = "P-1"
cfg.software_version = "PhoneOS 1.0"

# (label, scale) choices of the Text size control.
text_sizes = [
    (_("Small"), 0.85),
    (_("Default"), 1.0),
    (_("Large"), 1.2),
]


def settings_chevron_size():
    """Size of the common/chevron art on tappable settings rows (it grows
    with the text size, like the row labels).
    """
    s = text_px(30)
    return (s, s)


def notifications_enabled():
    return store.persistent._phone_notifications is not False


def sounds_enabled():
    return store.persistent._phone_sounds is not False


# Screen actions --------------------------------------------------------------
#
# gui.rebuild() (run by set_theme and set_text_scale) rebuilds every style and
# restarts the interaction; the open phone is redrawn with the new styles.

class SetTheme(PhoneAction):
    """Switches the phone theme, e.g. SetTheme("dark")."""

    def __init__(self, name):
        self.name = name

    def run(self):
        if theme_name() != self.name:
            set_theme(self.name)

    def get_selected(self):
        return theme_name() == self.name


class SetTextScale(PhoneAction):
    """Changes the phone text size, e.g. SetTextScale(1.2)."""

    def __init__(self, scale):
        self.scale = scale

    def run(self):
        if abs(text_scale() - self.scale) > 0.001:
            set_text_scale(self.scale)

    def get_selected(self):
        return abs(text_scale() - self.scale) < 0.001


class SetPreference(PhoneAction):
    """Sets persistent._phone_<name>, e.g. SetPreference("sounds", False)."""

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def run(self):
        setattr(store.persistent, "_phone_" + self.name, self.value)

    def get_selected(self):
        return getattr(store.persistent, "_phone_" + self.name) == self.value


# Settings added by the game --------------------------------------------------

custom_settings = []  # ToggleSetting / ActionSetting, in the order added


def _get_path(obj, path):
    for part in path.split("."):
        obj = getattr(obj, part)
    return obj


class ToggleSetting(python_object):
    """A switch bound to a store or persistent variable (see add_toggle_setting)."""

    def __init__(self, label, variable, description=None, persistent=False, section=None,
                 true_value=True, false_value=False):
        self.label = label
        self.variable = variable
        self.description = description
        self.persistent = persistent
        self.section = section
        self.true_value = true_value
        self.false_value = false_value

    def value(self):
        obj = store.persistent if self.persistent else store
        try:
            return _get_path(obj, self.variable) == self.true_value
        except AttributeError:
            return False

    def action(self):
        if self.persistent:
            return store.ToggleField(store.persistent, self.variable, self.true_value, self.false_value)
        return ToggleStoreSetting(self.variable, self.true_value, self.false_value)


class ToggleStoreSetting(PhoneAction):
    """ToggleVariable that also keeps the change if the game is saved while
    the phone is still open (story variables are saved; see PhoneAction).
    """

    def __init__(self, variable, true_value=True, false_value=False):
        self.variable = variable
        self.true_value = true_value
        self.false_value = false_value

    def _toggle(self):
        return store.ToggleVariable(self.variable, self.true_value, self.false_value)

    def run(self):
        self._toggle()()

    def get_selected(self):
        return self._toggle().get_selected()


class ActionSetting(python_object):
    """A tappable row that runs an action (see add_action_setting)."""

    def __init__(self, label, action, description=None, section=None):
        self.label = label
        self._action = action
        self.description = description
        self.section = section

    def action(self):
        return self._action


def _add_setting(setting):
    for i, s in enumerate(custom_settings):
        if s.label == setting.label and s.section == setting.section:
            custom_settings[i] = setting
            return setting
    custom_settings.append(setting)
    return setting


def add_toggle_setting(label, variable, description=None, persistent=False, section=None,
                       true_value=True, false_value=False):
    """Adds an on/off row for a game variable to the Settings app.

    Call it from an init block:

        default spoilers = False
        init python:
            phone.add_toggle_setting(_("Show hints"), "spoilers")
            phone.add_toggle_setting(_("Skip calls"), "skip_calls", persistent=True,
                                     description=_("Shared by all saves"))

    `label`
        Row title (wrap in _() to translate).
    `variable`
        Name of the variable the switch flips, as a string. A store
        variable ("hints", or "mystore.hints" for a named store) is saved
        with the game; with `persistent` True it is a field of `persistent`
        and is shared by every save.
    `description`
        Optional second line.
    `section`
        Section title; rows without one go in a "Game" section. Sections
        appear in the order their first row was added.
    `true_value`, `false_value`
        Values for on and off (default True and False).

    Only the variable name is stored, so nothing here ends up in save files.
    Adding a row with the same label and section again replaces it.
    """
    init_only("phone.add_toggle_setting()")
    return _add_setting(ToggleSetting(label, variable, description, persistent, section, true_value, false_value))


def add_action_setting(label, action, description=None, section=None):
    """Adds a tappable row that runs a Ren'Py action (e.g. ShowMenu("preferences"))."""
    init_only("phone.add_action_setting()")
    check_picklable(action, "phone.add_action_setting action")
    return _add_setting(ActionSetting(label, action, description, section))


def remove_setting(label, section=None):
    init_only("phone.remove_setting()")
    custom_settings[:] = [s for s in custom_settings if not (s.label == label and s.section == section)]


def custom_setting_sections():
    """[(section title, [settings])] for the rows games added, in order."""
    rv = []
    index = {}
    for s in custom_settings:
        title = s.section or _("Game")
        if title not in index:
            index[title] = len(rv)
            rv.append((title, []))
        rv[index[title]][1].append(s)
    return rv


def _settings_lint():
    for s in custom_settings:
        if isinstance(s, ToggleSetting) and not s.persistent:
            try:
                _get_path(store, s.variable)
            except AttributeError:
                print("phone: settings toggle {!r} uses variable {!r}, which does not exist (add a default).".format(s.label, s.variable))


if _settings_lint not in store.config.lint_hooks:
    store.config.lint_hooks.append(_settings_lint)


"""renpy
init -910 python in phone:
"""


class SettingsApp(App):
    id = "settings"
    name = _("Settings")
    screen = "phone_settings"
    order = 90


register_app(SettingsApp())

require_art("settings/segmented", "settings/segment", "settings/thumbnail_mask", "common/chevron")
