"""renpy
init -930 python in phone:
"""

# Displayable helpers used by the phone screens (and handy for custom apps).

from store import AlphaMask, Fixed, Frame, Solid, Text, Transform

GLYPH_FONT = "DejaVuSans.ttf"  # ships with Ren'Py, has the symbols we use

# Symbols that render as plain glyphs in DejaVu Sans. Many others (such as
# the envelope, gear, black telephone or left-pointing triangle) are drawn as
# color emoji by Ren'Py 8.2+, so App.glyph should come from this set:
#   ❝ ◉ ✆ ☏ ✱ ◐ ✎ ♡ ❖ ⌂ ▣ ▦ ◈ ✦ ☰ ≡ ♫ ⚑ ⊙ ✚ ‹ › ○ ● ✕

# Screens are re-evaluated on every interaction, so rebuilding avatars, icons
# and cropped images each time adds up with long chat logs and feeds. Builders
# below cache their result on everything it depends on. Not saved.
_memo = {}


def memoized(fn):
    """Caches fn(*args) per theme, text size and resolution."""

    def wrapper(*args):
        key = (fn.__name__, args, theme_name(), text_scale(), store.config.screen_height)
        try:
            rv = _memo.get(key)
        except TypeError:  # unhashable argument
            return fn(*args)
        if rv is None:
            if len(_memo) > 4000:
                _memo.clear()
            rv = _memo[key] = fn(*args)
        return rv

    wrapper.__name__ = fn.__name__
    wrapper.__qualname__ = fn.__qualname__
    wrapper.__module__ = fn.__module__
    wrapper.__doc__ = fn.__doc__
    return wrapper


# Folder holding the framework images, relative to the game directory.
asset_dir = "phone/images/"


def asset(name):
    return asset_dir + name


@memoized
def rounded(key_or_color, radius="md"):
    """A rounded rectangle Frame in a theme color. radius: "sm", "md" or "lg"."""
    image, border = {
        "sm": ("round_8.png", 8),
        "md": ("round_18.png", 18),
        "lg": ("round_48.png", 48),
    }[radius]
    scale = px(1000) / 1000.0
    return Frame(Transform(tinted(asset(image), key_or_color), zoom=scale), px(border), px(border))


@memoized
def circle(key_or_color, size):
    return Transform(tinted(asset("circle.png"), key_or_color), xysize=(size, size))


@memoized
def cover(image, width, height):
    """Scales `image` to fill width x height, cropping the overflow evenly."""
    width, height = int(width), int(height)
    scaled = Transform(image, fit="cover", xysize=(width, height))
    centered = Fixed(Transform(scaled, align=(0.5, 0.5)), xysize=(width, height))
    return Transform(centered, crop=(0, 0, width, height))


def avatar(who, size):
    """Round avatar for a Contact, a contact id, or None for the player."""
    size = int(size)
    if who is None:
        image = cfg.player_avatar
        tint = color("accent")
        initial = (player_name() or "?")[:1].upper()
    else:
        c = contact(who)
        image = c.avatar
        tint = c.tint()
        initial = c.initial()
    return _avatar(image, tint, initial, size)


@memoized
def _avatar(image, tint, initial, size):
    if image is None:
        return Fixed(
            circle(tint, size),
            Text(initial, substitute=False, size=int(size * 0.45), color="#ffffff", bold=True, xalign=0.5, yalign=0.5),
            xysize=(size, size),
        )

    return AlphaMask(
        cover(image, size, size),
        Transform(asset("circle.png"), xysize=(size, size)),
    )


@memoized
def app_icon(app, size):
    size = int(size)
    if app.icon is not None:
        return Transform(app.icon, fit="contain", xysize=(size, size))
    return Fixed(
        Transform(tinted(asset("app_icon.png"), app.color), xysize=(size, size)),
        Text(app.glyph, font=GLYPH_FONT, size=int(size * 0.5), color="#ffffff", xalign=0.5, yalign=0.5),
        xysize=(size, size),
    )


def wallpaper_image():
    """The current wallpaper displayable, or None for the theme color."""
    for wid in (state.wallpaper, cfg.default_wallpaper):
        for w in cfg.wallpapers:
            if wid is not None and w[0] == wid:
                return w[1]
    return None


def is_image(value):
    """True if a message/post payload names an image rather than text."""
    if not isinstance(value, str):
        return value is not None
    return renpy.has_image(value) or (renpy.loadable(value) and not value.endswith((".txt", ".rpy")))


# Full-display backgrounds for app screens (e.g. a call screen). While such a
# screen is showing, the background is drawn behind the whole display and the
# status and navigation bars become transparent, as on the home screen.
screen_backgrounds = {}  # screen name -> displayable, color or theme key


def set_screen_background(screen, background):
    """Registers a full-display background for `screen` (call at init time).

    `background` is a displayable, a color such as "#101010", or a theme
    key such as "bg". None removes it.
    """
    if background is None:
        screen_backgrounds.pop(screen, None)
    else:
        screen_backgrounds[screen] = background


def screen_background(screen):
    """The displayable to draw behind `screen`, or None."""
    bg = screen_backgrounds.get(screen)
    if bg is None:
        return None
    if isinstance(bg, str) and (bg in theme() or bg in cfg.themes.get("light", {})):
        return Solid(color(bg))
    if isinstance(bg, str) and bg.startswith("#"):
        return Solid(bg)
    return cover(bg, *display_size())


# Geometry of the display, in real pixels. Custom app screens can use these.

def display_size():
    return px(cfg.width - 2 * cfg.bezel), px(cfg.height - 2 * cfg.bezel)


STATUS_HEIGHT = 40
NAV_HEIGHT = 52
HEADER_HEIGHT = 72


def content_size():
    """Space available to an app screen, between status and nav bars."""
    w, h = display_size()
    return w, h - px(STATUS_HEIGHT) - px(NAV_HEIGHT)


def page_body_height():
    """Height below a phone_page header."""
    return content_size()[1] - px(HEADER_HEIGHT)


def _clock_frame(st, at, style, color):
    kwargs = {"color": color} if color else {}
    rv = Text(clock_text(), style=style, substitute=False, **kwargs)
    # Tick once a second for the real-time clock; a story clock is static.
    return rv, (1.0 if state.clock is None else None)


def clock(style="phone_status_text", color=None):
    """The status bar clock as a displayable that updates itself.

    (A screen timer would re-run the whole phone screen every second.)
    """
    return store.DynamicDisplayable(_clock_frame, style, color)
