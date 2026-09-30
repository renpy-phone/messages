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

from store import Color as _Color, Fixed as _Fixed, Solid as _Solid, Transform as _Transform, TintMatrix as _TintMatrix


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
        raise Exception("phone: unknown wallpaper {!r} (add it with phone.add_wallpaper).".format(id))
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


def wallpaper_thumbnail(id, width, height, radius="md", dim=False):
    """A rounded preview of a wallpaper, e.g. for a settings row.

    `id` None (or an unknown id) shows the theme's wallpaper color.
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
            _Transform(rounded("#ffffff", radius), xysize=size),
        ),
        xysize=size,
    )


def wallpaper_tile_size():
    """Size of a wallpaper preview in the app's two-column grid."""
    dw, dh = display_size()
    tw = px(168)
    return tw, int(round(tw * dh / float(dw)))


# Turns a white-on-black drawing into white on transparent, so shapes can be
# cut out of each other (used for the padlock's shackle).
_BLACK_TO_CLEAR = store.Matrix([1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0])


def lock_icon(size):
    """A white padlock drawn from plain shapes (no emoji font needed)."""
    size = int(size)
    t = max(2, int(round(size * 0.12)))  # stroke
    sw = int(round(size * 0.56))  # shackle width
    sx = (size - sw) // 2
    bw = int(round(size * 0.8))  # body
    bh = int(round(size * 0.5))
    by = size - bh
    arch = _Transform(
        _Fixed(
            _Transform(asset("circle.png"), xysize=(sw, sw)),
            _Transform(asset("circle.png"), xysize=(sw - 2 * t, sw - 2 * t), matrixcolor=_TintMatrix("#000000"), align=(0.5, 0.5)),
            xysize=(sw, sw),
        ),
        mesh=True, matrixcolor=_BLACK_TO_CLEAR, crop=(0, 0, sw, sw // 2),
    )
    legs = by - sw // 2 + t
    return _Fixed(
        _Transform(arch, xpos=sx, ypos=0),
        _Solid("#ffffff", xysize=(t, legs), xpos=sx, ypos=sw // 2),
        _Solid("#ffffff", xysize=(t, legs), xpos=sx + sw - t, ypos=sw // 2),
        _Transform(rounded("#ffffff", "sm"), xysize=(bw, bh), xpos=(size - bw) // 2, ypos=by),
        xysize=(size, size),
    )


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
# Drawn from Solids and the white shapes in phone/images, so they need no
# image files. They are authored on a 540x1140 canvas (the display's shape)
# and scaled to fit.

WALLPAPER_SIZE = (540, 1140)


def gradient(colors, width=WALLPAPER_SIZE[0], height=WALLPAPER_SIZE[1], steps=72):
    """A vertical gradient through `colors` (top to bottom), made of bands."""
    colors = [_Color(c) for c in colors]
    if len(colors) == 1:
        return _Solid(colors[0], xysize=(width, height))
    band = height / float(steps)
    children = []
    for i in range(steps):
        t = (i + 0.5) / steps * (len(colors) - 1)
        k = min(int(t), len(colors) - 2)
        c = colors[k].interpolate(colors[k + 1], t - k)
        y0 = int(round(i * band))
        y1 = int(round((i + 1) * band))
        children.append(_Solid(c, xysize=(width, y1 - y0 + 1), ypos=y0))
    return _Fixed(*children, xysize=(width, height))


def _shape(image, tint, size, x, y, alpha=1.0):
    """A tinted white shape centered on (x, y) of the canvas."""
    return _Transform(
        asset(image), xysize=(size, size), matrixcolor=_TintMatrix(tint),
        alpha=alpha, xpos=x, ypos=y, xanchor=0.5, yanchor=0.5,
    )


def _canvas(*children):
    w, h = WALLPAPER_SIZE
    return _Transform(_Fixed(*children, xysize=(w, h)), crop=(0, 0, w, h))


def _builtin_wallpapers():
    w, h = WALLPAPER_SIZE

    aurora = _canvas(
        gradient(["#0f2027", "#203a43", "#2c5364"]),
        _shape("circle.png", "#43cea2", 560, 60, 330, 0.28),
        _shape("circle.png", "#185a9d", 680, 470, 720, 0.35),
        _shape("circle.png", "#7f7fd5", 360, 420, 180, 0.18),
    )

    dusk = _canvas(
        gradient(["#1a1a40", "#6a2c70", "#e3646b", "#f9b17a"]),
        _shape("circle.png", "#ffe29a", 250, 270, 790, 0.95),
        _shape("circle.png", "#3b1f4a", 1100, 30, 1400),
        _shape("circle.png", "#2a1537", 1000, 560, 1440),
    )

    stars = []
    rng = _random.Random(7)
    for _i in range(34):
        size = rng.choice((4, 5, 6, 8))
        stars.append(_shape("circle.png", "#ffffff", size, rng.randint(10, w - 10), rng.randint(10, int(h * 0.7)), rng.uniform(0.35, 0.9)))
    night = _canvas(
        gradient(["#070b1d", "#16224a", "#34467f"]),
        *(stars + [
            _shape("circle.png", "#f6f1d5", 150, 385, 330),
            _shape("circle.png", "#101838", 132, 420, 310),
            _shape("circle.png", "#0d1530", 900, 100, 1500),
            _shape("circle.png", "#111b3b", 900, 520, 1560),
        ])
    )

    lagoon = _canvas(
        gradient(["#0b6e70", "#139a86", "#2bb884"]),
        _shape("ring.png", "#ffffff", 420, 470, 250, 0.22),
        _shape("ring.png", "#ffffff", 260, 470, 250, 0.16),
        _shape("ring.png", "#ffffff", 600, 60, 900, 0.18),
        _shape("circle.png", "#ffffff", 180, 90, 520, 0.08),
    )

    coral = _canvas(
        gradient(["#c0265f", "#e8566a", "#f98f6f"]),
        _shape("circle.png", "#ffffff", 520, 470, 180, 0.12),
        _shape("circle.png", "#ffffff", 400, 40, 620, 0.10),
        _shape("circle.png", "#ffd3a5", 420, 520, 1040, 0.25),
    )

    graphite = _canvas(
        gradient(["#1c1d20", "#2c2e33", "#3d4046"]),
        *[_shape("ring.png", "#ffffff", s, 540, 1140, 0.07) for s in (300, 520, 740, 960, 1180, 1400)]
    )

    return [
        ("aurora", aurora, _("Aurora")),
        ("dusk", dusk, _("Dusk")),
        ("night", night, _("Night Sky")),
        ("lagoon", lagoon, _("Lagoon")),
        ("coral", coral, _("Coral")),
        ("graphite", graphite, _("Graphite")),
    ]


for _w in _builtin_wallpapers():
    add_wallpaper(*_w)
del _w

cfg.default_wallpaper = "aurora"


def _wallpapers_lint():
    if cfg.default_wallpaper is not None and wallpaper_entry(cfg.default_wallpaper) is None:
        print("phone: cfg.default_wallpaper {!r} is not in cfg.wallpapers.".format(cfg.default_wallpaper))
    for w in cfg.wallpapers:
        if isinstance(w[1], str) and not renpy.has_image(w[1]) and not renpy.loadable(w[1]):
            print("phone: wallpaper {!r} uses image {!r}, which does not exist.".format(w[0], w[1]))


if _wallpapers_lint not in store.config.lint_hooks:
    store.config.lint_hooks.append(_wallpapers_lint)


"""renpy
init -910 python in phone:
"""


class WallpapersApp(App):
    id = "wallpapers"
    name = _("Wallpapers")
    screen = "phone_wallpapers"
    glyph = "◐"
    color = "#ff9500"
    order = 80

    def badge(self):
        return len([i for i in wallpapers_state.new if wallpaper_entry(i) is not None])

    def reset(self):
        global wallpapers_state
        wallpapers_state = WallpapersState()


register_app(WallpapersApp())


"""renpy
default phone.wallpapers_state = phone.WallpapersState()
"""
