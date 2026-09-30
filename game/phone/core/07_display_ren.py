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

# Folder holding the framework images, relative to the game directory.
asset_dir = "phone/images/"


def asset(name):
    return asset_dir + name


def rounded(key_or_color, radius="md"):
    """A rounded rectangle Frame in a theme color. radius: "sm", "md" or "lg"."""
    image, border = {
        "sm": ("round_8.png", 8),
        "md": ("round_18.png", 18),
        "lg": ("round_48.png", 48),
    }[radius]
    scale = px(1000) / 1000.0
    return Frame(Transform(tinted(asset(image), key_or_color), zoom=scale), px(border), px(border))


def circle(key_or_color, size):
    return Transform(tinted(asset("circle.png"), key_or_color), xysize=(size, size))


def cover(image, width, height):
    """Scales and crops `image` to fill width x height."""
    return Transform(image, fit="cover", xysize=(width, height), crop_relative=True)


def avatar(who, size):
    """Round avatar for a Contact, a contact id, or None for the player."""
    size = int(size)
    if who is None:
        image = cfg.player_avatar
        tint = color("accent")
        initial = (cfg.player_name or "?")[:1].upper()
    else:
        c = contact(who)
        image = c.avatar
        tint = c.tint()
        initial = c.initial()

    if image is None:
        return Fixed(
            circle(tint, size),
            Text(initial, substitute=False, size=int(size * 0.45), color="#ffffff", bold=True, xalign=0.5, yalign=0.5),
            xysize=(size, size),
        )

    return AlphaMask(
        Transform(image, fit="cover", xysize=(size, size)),
        Transform(asset("circle.png"), xysize=(size, size)),
    )


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
    wid = state.wallpaper or cfg.default_wallpaper
    for w in cfg.wallpapers:
        if w[0] == wid:
            return w[1]
    return None


def is_image(value):
    """True if a message/post payload names an image rather than text."""
    if not isinstance(value, str):
        return value is not None
    return renpy.has_image(value) or (renpy.loadable(value) and not value.endswith((".txt", ".rpy")))


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
