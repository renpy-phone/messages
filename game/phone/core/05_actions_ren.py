"""renpy
init -950 python in phone:
"""

# Screen actions. Every change to phone state made from a screen goes
# through an action so it survives save/load mid-interaction.

from store import Action, DictEquality  # pyright: ignore[reportMissingImports]

_called = False  # True while phone.open() is waiting in call_screen


class PhoneAction(Action, DictEquality):
    def __call__(self):
        self.run()
        mutated()

    def run(self):
        raise NotImplementedError


class Launch(PhoneAction):
    """Opens an app, optionally at one of its inner screens."""

    def __init__(self, app_id, screen=None, **kwargs):
        self.app_id = app_id
        self.screen = screen
        self.kwargs = kwargs

    def run(self):
        play_sound("tap")
        state.launch(self.app_id, self.screen, **self.kwargs)


class Navigate(PhoneAction):
    """Pushes a screen of the current app, e.g. a conversation."""

    def __init__(self, screen, **kwargs):
        self.screen = screen
        self.kwargs = kwargs

    def run(self):
        state.navigate(self.screen, **self.kwargs)


class Back(PhoneAction):
    def run(self):
        state.back()


class Home(PhoneAction):
    def run(self):
        state.home()


class Close(Action, DictEquality):
    """Closes the phone, returning from phone.open() if it was used."""

    def __call__(self):
        global _called
        if _called:
            _called = False
            return True  # ends the call_screen interaction
        renpy.hide_screen("phone", layer=cfg.layer)
        renpy.restart_interaction()


class Show(Action, DictEquality):
    """Opens the phone without blocking the script (for buttons and keys)."""

    def __init__(self, app_id=None, screen=None, **kwargs):
        self.app_id = app_id
        self.screen = screen
        self.kwargs = kwargs

    def __call__(self):
        show(self.app_id, self.screen, **self.kwargs)

    def get_sensitive(self):
        return state.enabled


class Toggle(Action, DictEquality):
    """Opens the phone if it is closed and closes it if it is open."""

    def __call__(self):
        if is_open():
            return Close()()
        show()

    def get_sensitive(self):
        return state.enabled or is_open()


class Dismiss(Action, DictEquality):
    """Goes back one screen, or closes the phone from the home screen."""

    def __call__(self):
        if state.nav:
            Back()()
        else:
            return Close()()
