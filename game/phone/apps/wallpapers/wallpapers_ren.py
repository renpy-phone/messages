"""renpy
init -920 python in phone:
"""

# Wallpapers app: a registry of wallpapers (static, defined at init time),
# the saved list of unlocked ones, and the actions used by its screens.
#
# Add wallpapers from an init block:
#
#     init python:
#         phone.add_wallpaper("beach", "bg beach", _("Beach"))
#         phone.add_wallpaper("her_photo", "cg lucy selfie", _("Lucy"), locked=True)
#
# and unlock the locked ones during the story:
#
#     $ phone.unlock_wallpaper("her_photo")
#
# The current wallpaper is saved in phone.state.wallpaper (None means
# cfg.default_wallpaper).

import random as _random

from store import (
    Color as _Color,
    Fixed as _Fixed,
    Solid as _Solid,
    Transform as _Transform,
    TintMatrix as _TintMatrix,
)  # pyright: ignore[reportMissingImports]


# Registry --------------------------------------------------------------------


def _entry(item):
    """Normalizes a cfg.wallpapers item to (id, image, name, locked).

    Games may append plain (id, image, name) tuples to cfg.wallpapers; those
    are unlocked from the start.
    """
    wid = item[0]
    image = item[1]
    name = item[2] if len(item) > 2 and item[2] else wid.replace("_", " ").title()
    locked = bool(item[3]) if len(item) > 3 else False
    return wid, image, name, locked


def add_wallpaper(id, image, name=None, locked=False):
    """Adds a wallpaper the player can pick. Call from an init block.

    `id`
        A unique, stable string. Saves refer to wallpapers by id.
    `image`
        An image name or any displayable. It is scaled and cropped to fill
        the phone display, so a portrait image about 1:2 looks best.
    `name`
        Name shown in the Wallpapers app. Defaults to the id, titled.
    `locked`
        When True the player must unlock it first with
        phone.unlock_wallpaper(id).

    Adding an id that already exists replaces that wallpaper, which lets a
    game restyle a built-in one.
    """
    init_only("phone.add_wallpaper()")
    item = (id, image, name, locked)
    for i, w in enumerate(cfg.wallpapers):
        if w[0] == id:
            cfg.wallpapers[i] = item
            return id
    cfg.wallpapers.append(item)
    return id


def remove_wallpaper(id):
    """Removes a wallpaper from the registry. Call from an init block."""
    init_only("phone.remove_wallpaper()")
    cfg.wallpapers[:] = [w for w in cfg.wallpapers if w[0] != id]
    if cfg.default_wallpaper == id:
        cfg.default_wallpaper = None


def clear_wallpapers():
    """Removes every wallpaper, including the built-in ones (init time)."""
    init_only("phone.clear_wallpapers()")
    cfg.wallpapers[:] = []
    cfg.default_wallpaper = None


def all_wallpapers():
    """Every wallpaper as a list of (id, image, name, locked) tuples."""
    return [_entry(w) for w in cfg.wallpapers]


def wallpaper_entry(id):
    """(id, image, name, locked) for a wallpaper id, or None."""
    for w in cfg.wallpapers:
        if w[0] == id:
            return _entry(w)
    return None


def wallpaper_name(id):
    e = wallpaper_entry(id)
    return e[2] if e is not None else ""


# Saved state -----------------------------------------------------------------


class WallpapersState(object):
    def __init__(self):
        self.version = 1
        self.unlocked = []  # ids of locked wallpapers the player has unlocked
        self.new = []  # unlocked ids the player has not looked at yet


def _wallpapers_after_load():
    s = globals().get("wallpapers_state")
    if s is None:
        return
    for k, v in WallpapersState().__dict__.items():
        if not hasattr(s, k):
            setattr(s, k, v)


if _wallpapers_after_load not in store.config.after_load_callbacks:
    store.config.after_load_callbacks.append(_wallpapers_after_load)


# Public API ------------------------------------------------------------------


def _require(id):
    e = wallpaper_entry(id)
    if e is None:
        raise Exception(
            "phone: unknown wallpaper {!r} (add it with phone.add_wallpaper).".format(
                id
            )
        )
    return e


def wallpaper_unlocked(id):
    """True if the wallpaper exists and the player may use it."""
    e = wallpaper_entry(id)
    if e is None:
        return False
    return not e[3] or id in wallpapers_state.unlocked


def wallpaper_is_new(id):
    return id in wallpapers_state.new


def unlock_wallpaper(id, notify=True):
    """Unlocks a locked wallpaper. Returns True if it was locked before.

    With `notify` a "New wallpaper unlocked" banner is shown (while the phone
    is closed) and the app gets a badge until the player looks at it.
    """
    e = _require(id)
    if wallpaper_unlocked(id):
        return False
    wallpapers_state.unlocked.append(id)
    if id not in wallpapers_state.new:
        wallpapers_state.new.append(id)
    if notify:
        globals()["notify"](_("New wallpaper unlocked"), e[2], app_id="wallpapers")
    return True


def lock_wallpaper(id):
    """Locks a `locked=True` wallpaper again; if it was current, the default returns."""
    _require(id)
    if id in wallpapers_state.unlocked:
        wallpapers_state.unlocked.remove(id)
    if id in wallpapers_state.new:
        wallpapers_state.new.remove(id)
    if state.wallpaper == id and not wallpaper_unlocked(id):
        state.wallpaper = None


def set_wallpaper(id):
    """Makes `id` the home screen wallpaper. None goes back to the default.

    Setting a locked wallpaper from the script unlocks it silently, so the
    story can change the wallpaper for the player.
    """
    if id is None:
        state.wallpaper = None
        return
    _require(id)
    if not wallpaper_unlocked(id):
        wallpapers_state.unlocked.append(id)
    if id in wallpapers_state.new:
        wallpapers_state.new.remove(id)
    state.wallpaper = id


def current_wallpaper():
    """The id of the wallpaper on the home screen, or None for the theme color."""
    for wid in (state.wallpaper, cfg.default_wallpaper):
        if wid is not None and wallpaper_entry(wid) is not None:
            return wid
    return None


def wallpaper_thumbnail(id, width, height, mask=("wallpapers/mask", 18), dim=False):
    """A rounded preview of a wallpaper, e.g. for a settings row.

    `id` None (or an unknown id) shows the theme's wallpaper color. `mask`
    is (art name, 9-slice border) of the white shape that rounds it.
    """
    e = wallpaper_entry(id) if id is not None else None
    size = (int(width), int(height))
    if e is None:
        image = _Solid(color("wallpaper"), xysize=size)
    else:
        image = cover(e[1], *size)
    if dim:
        image = _Fixed(image, _Solid("#000000a0"), xysize=size)
    return _Fixed(
        store.AlphaMask(
            _Transform(image, xysize=size),
            _Transform(art_frame(*mask), xysize=size),
        ),
        xysize=size,
    )


def wallpaper_tile_size():
    """Size of a wallpaper preview in the app's two-column grid."""
    dw, dh = display_size()
    tw = px(168)
    return tw, int(round(tw * dh / float(dw)))


def wallpaper_preview_image(id):
    """The wallpaper as the home screen crops it, for the app's content area."""
    e = wallpaper_entry(id)
    cw, ch = content_size()
    if e is None:
        return _Solid(color("wallpaper"), xysize=(cw, ch))
    full = cover(e[1], *display_size())
    return _Transform(full, crop=(0, px(STATUS_HEIGHT), cw, ch))


# Screen actions --------------------------------------------------------------


class PreviewWallpaper(PhoneAction):
    """Opens the full-display preview of a wallpaper."""

    def __init__(self, id):
        self.id = id

    def run(self):
        if self.id in wallpapers_state.new:
            wallpapers_state.new.remove(self.id)
        state.navigate("phone_wallpapers_preview", wallpaper=self.id)


class SetWallpaper(PhoneAction):
    """Makes a wallpaper current and returns from its preview to the grid."""

    def __init__(self, id):
        self.id = id

    def run(self):
        set_wallpaper(self.id)
        play_sound("tap")
        if state.current()[0] == "phone_wallpapers_preview":
            state.back()

    def get_sensitive(self):
        return wallpaper_unlocked(self.id)

    def get_selected(self):
        return current_wallpaper() == self.id


# Built-in wallpapers ---------------------------------------------------------
#
# Pictures in gui/phone/wallpapers/ (drawn by tools/art/wallpapers_art.rpy).
# A game can restyle one by adding a wallpaper with the same id, or remove
# them with phone.clear_wallpapers().

for _wid, _wname in (
    ("aurora", _("Aurora")),
    ("dusk", _("Dusk")),
    ("night", _("Night Sky")),
    ("lagoon", _("Lagoon")),
    ("coral", _("Coral")),
    ("graphite", _("Graphite")),
):
    add_wallpaper(_wid, "gui/phone/wallpapers/{}.png".format(_wid), _wname)
del _wid, _wname

cfg.default_wallpaper = "aurora"


def _wallpapers_lint():
    if (
        cfg.default_wallpaper is not None
        and wallpaper_entry(cfg.default_wallpaper) is None
    ):
        print(
            "phone: cfg.default_wallpaper {!r} is not in cfg.wallpapers.".format(
                cfg.default_wallpaper
            )
        )
    for w in cfg.wallpapers:
        if (
            isinstance(w[1], str)
            and not renpy.has_image(w[1])
            and not renpy.loadable(w[1])
        ):
            print(
                "phone: wallpaper {!r} uses image {!r}, which does not exist.".format(
                    w[0], w[1]
                )
            )


if _wallpapers_lint not in store.config.lint_hooks:
    store.config.lint_hooks.append(_wallpapers_lint)


"""renpy
init -910 python in phone:
"""


class WallpapersApp(App):
    id = "wallpapers"
    name = _("Wallpapers")
    screen = "phone_wallpapers"
    order = 80

    def badge(self):
        return len([i for i in wallpapers_state.new if wallpaper_entry(i) is not None])

    def reset(self):
        global wallpapers_state
        wallpapers_state = WallpapersState()


register_app(WallpapersApp())

require_art(
    "wallpapers/tile",
    "wallpapers/mask",
    "wallpapers/lock",
    "wallpapers/set_button",
    "wallpapers/cancel_button",
    "common/check",
    "common/badge",
)


"""renpy
default phone.wallpapers_state = phone.WallpapersState()
"""
