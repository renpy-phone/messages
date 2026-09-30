"""renpy
init -990 python in phone:
"""

# Shared helpers for every part of the phone framework.
#
# All framework code lives in the `phone` named store, so games reach it as
# `phone.<name>` and nothing leaks into the default store.

import store
from renpy.compat.pickle import dumps as _pickle_dumps

# Sizes in the framework are authored for a 1080 pixel tall game and scaled to
# the real game height, so the phone looks the same at 720p, 1080p or 4K.
REFERENCE_HEIGHT = 1080.0


def px(n):
    """Scales a size authored at 1080p to the game's resolution."""
    return int(round(n * store.config.screen_height / REFERENCE_HEIGHT))


def text_px(n):
    """Like px(), but also applies the player's text size setting."""
    return px(n * text_scale())


def text_scale():
    return store.persistent._phone_text_scale or 1.0


def theme_name():
    name = store.persistent._phone_theme or cfg.default_theme
    if name not in cfg.themes:
        name = cfg.default_theme
    return name


def theme():
    return cfg.themes[theme_name()]


def color(key):
    """Returns a color of the active theme, e.g. phone.color("accent")."""
    t = theme()
    if key in t:
        return t[key]
    return cfg.themes["light"].get(key, "#f0f")


def tinted(image, key_or_color):
    """A white placeholder image tinted to a theme key or explicit color."""
    c = color(key_or_color) if not key_or_color.startswith("#") else key_or_color
    return store.Transform(image, matrixcolor=store.TintMatrix(c))


def run_effects(effects):
    """Runs a list of Ren'Py actions (SetVariable, Function, Jump, ...)."""
    for effect in effects or ():
        renpy.run(effect)


def check_picklable(obj, what):
    """In developer mode, fail loudly where an unpicklable effect is added.

    Anything stored in phone state ends up in save files, so lambdas and
    nested functions would otherwise break saving much later.
    """
    if not store.config.developer:
        return
    try:
        _pickle_dumps(obj)
    except Exception as e:
        raise TypeError(
            "{} must be picklable to be saved (use a Ren'Py action such as "
            "SetVariable or Function with a module-level function): {!r} ({})".format(what, obj, e)
        )


def as_list(value):
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]


def mutated():
    """Call after changing phone state from a screen action.

    Keeps the change when the player saves and loads mid-interaction, and
    redraws screens that display it.
    """
    renpy.retain_after_load()
    renpy.restart_interaction()
