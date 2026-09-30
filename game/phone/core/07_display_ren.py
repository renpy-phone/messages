"""renpy
init -930 python in phone:
"""

# Displayable helpers used by the phone screens (and handy for custom apps).

from store import AlphaMask, Fixed, Frame, Solid, Text, Transform

# Screens are re-evaluated on every interaction, so rebuilding avatars, icons
# and cropped images each time adds up with long chat logs and feeds. Builders
# below cache their result on everything it depends on. Not saved.
_display_cache = {}


def memoized(fn):
    """Caches fn(*args) per theme, text size and resolution."""

    def wrapper(*args):
        key = (fn.__name__, args, theme_name(), text_scale(), store.config.screen_height)
        try:
            rv = _display_cache.get(key)
        except TypeError:  # unhashable argument
            return fn(*args)
        if rv is None:
            if len(_display_cache) > 4000:
                _display_cache.clear()
            rv = _display_cache[key] = fn(*args)
        return rv

    wrapper.__name__ = fn.__name__
    wrapper.__qualname__ = fn.__qualname__
    wrapper.__module__ = fn.__module__
    wrapper.__doc__ = fn.__doc__
    return wrapper


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
    mask = art("common/avatar_mask", size=(size, size), fit="fill")
    if image is None:
        # No picture: the default avatar art with the contact's initial.
        return Fixed(
            art("common/avatar_default", size=(size, size), fit="fill"),
            Text(initial, style="phone_avatar_initial", substitute=False, size=int(size * 0.45), xalign=0.5, yalign=0.5),
            xysize=(size, size),
        )

    return AlphaMask(cover(image, size, size), mask)


@memoized
def app_icon(app, size, state="idle"):
    """The app's home screen icon: App.icon, or its art in `state`."""
    size = int(size)
    if app.icon is not None:
        return Transform(app.icon, fit="contain", xysize=(size, size))
    return art(app.icon_art(), state, size=(size, size))


def app_icon_states(app, size):
    """Icon displayables for every button state, for an imagebutton."""
    return {state: app_icon(app, size, state) for state in STATES}


APP_ICON_SIZE = 72
APP_ICON_TOP = 10


@memoized
def app_button_backgrounds(app):
    """Background properties that draw the app icon in every button state."""
    size = px(APP_ICON_SIZE)
    rv = {}
    for state in STATES:
        key = "background" if state == "idle" else state + "_background"
        rv[key] = Fixed(
            Transform(app_icon(app, size, state), xalign=0.5, ypos=px(APP_ICON_TOP)),
            xfill=True, yfill=True,
        )
    return rv


def bar_art(name, on_wallpaper):
    """Art for the status or nav bar: `<area>/wallpaper/<icon>` is preferred
    over the wallpaper, falling back to the regular `<area>/<icon>`.
    """
    if on_wallpaper:
        area, _, icon = name.rpartition("/")
        return [area + "/wallpaper/" + icon, name]
    return name


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
