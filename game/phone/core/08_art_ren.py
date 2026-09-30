"""renpy
init -929 python in phone:
"""

# Art lookup. Every icon, frame and picture the phone draws is an image file
# under `gui_dir` (game/gui/phone/ by default), named by area:
#
#     gui/phone/nav/back_idle.png
#     gui/phone/nav/back_hover.png
#     gui/phone/apps/messages/icon_idle.png
#     gui/phone/themes/dark/messages/bubble_in_idle.png   (theme override)
#
# An image may come in these states. Only idle is required; a missing state
# falls back along the chain on the right:
#
#     idle
#     hover            -> idle
#     selected_idle    -> selected -> idle
#     selected_hover   -> selected_hover -> selected -> hover -> idle
#     insensitive      -> idle
#
# A file with no state suffix (e.g. `nav/back.png`) is accepted as idle.
# For each state, the active theme's folder (themes/<theme>/...) is checked
# before the shared one. Flat fills and text colors are not art: they come
# from the theme (cfg.themes).

gui_dir = "gui/phone/"
art_extensions = (".png", ".webp", ".jpg")

STATES = ("idle", "hover", "selected_idle", "selected_hover", "insensitive")

_STATE_FALLBACKS = {
    "idle": ("idle", ""),
    "hover": ("hover", "idle", ""),
    "selected_idle": ("selected_idle", "selected", "idle", ""),
    "selected_hover": ("selected_hover", "selected", "hover", "idle", ""),
    "insensitive": ("insensitive", "idle", ""),
}

_art_path_cache = {}
_missing_art = set()  # names reported as missing (for lint)


def _art_candidates(name, state):
    names = [name] if isinstance(name, str) else list(name)
    folders = ["themes/{}/".format(theme_name()), ""]
    for suffix in _STATE_FALLBACKS[state]:
        for n in names:
            for folder in folders:
                base = gui_dir + folder + n + ("_" + suffix if suffix else "")
                for ext in art_extensions:
                    yield base + ext


def art_path(name, state="idle"):
    """The file for art `name` in `state`, following the fallbacks, or None.

    `name` is a path under gui_dir without state or extension, such as
    "nav/back", or a list of such names tried in order (e.g. a specific
    variant first, then a general one).
    """
    key = (tuple(name) if not isinstance(name, str) else name, state, theme_name())
    if key in _art_path_cache:
        return _art_path_cache[key]
    rv = None
    for path in _art_candidates(name, state):
        if renpy.loadable(path):
            rv = path
            break
    _art_path_cache[key] = rv
    return rv


def has_art(name, state="idle"):
    return art_path(name, state) is not None


def _missing(name):
    label = name if isinstance(name, str) else " / ".join(name)
    if label not in _missing_art:
        _missing_art.add(label)
        if store.config.developer:
            print("phone: missing art {}{}_idle.png".format(gui_dir, label))
    # Visible in development, invisible in a release build.
    return Solid("#ff00ff80" if store.config.developer else "#0000")


def art(name, state="idle", size=None, fit="contain"):
    """A displayable for art `name` (see art_path), optionally sized.

    `size` is (width, height) in real pixels; the image is fitted with
    `fit` ("contain", "cover", "fill", ...).
    """
    path = art_path(name, state)
    d = path if path is not None else _missing(name)
    if size is not None:
        d = Transform(d, fit=fit, xysize=(int(size[0]), int(size[1])))
    return d


def art_states(name, size=None, fit="contain", prefix=""):
    """Style properties for every state of `name`, for use with `properties`.

    With prefix "" this gives idle/hover/... keys for an imagebutton:

        imagebutton:
            properties phone.art_states("nav/back", (phone.px(40), phone.px(40)))
            action phone.Back()

    With prefix "background" it gives background/hover_background/... for a
    button's background, and with "foreground" its foreground.
    """
    rv = {}
    for state in STATES:
        if prefix:
            key = prefix if state == "idle" else state + "_" + prefix
        else:
            key = state
        rv[key] = art(name, state, size, fit)
    return rv


def art_frame(name, borders, state="idle", tile=False):
    """A 9-slice Frame of art `name`. `borders` are in art pixels: an int, or
    (left, top, right, bottom). Art is drawn at 1080p scale and resized with
    the game (see px()).
    """
    if isinstance(borders, int):
        borders = (borders, borders, borders, borders)
    path = art_path(name, state)
    if path is None:
        return _missing(name)
    scale = px(1000) / 1000.0
    return Frame(Transform(path, zoom=scale), *[max(0, int(round(b * scale))) for b in borders], tile=tile)


def art_frame_states(name, borders, prefix="background", tile=False):
    """Like art_states(), for Frame backgrounds of a button."""
    rv = {}
    for state in STATES:
        key = prefix if state == "idle" else state + "_" + prefix
        rv[key] = art_frame(name, borders, state, tile)
    return rv


def clear_art_cache():
    """Forget which art files exist (after adding files at runtime)."""
    _art_path_cache.clear()
    _display_cache.clear()


# Art every game needs; apps add theirs with require_art(). Lint reports any
# whose idle image can't be found.
required_art = []


def require_art(*names):
    for n in names:
        if n not in required_art:
            required_art.append(n)


def art_layer_states(name, size, prefix="background", **placement):
    """Button background (or foreground) properties that draw art `name`,
    sized and placed inside the button, in every state. For example a toggle
    on the right of a settings row:

        button:
            properties phone.art_layer_states("common/toggle", (w, h), "foreground", xalign=1.0, yalign=0.5, xoffset=-16)
            selected value
    """
    rv = {}
    for state in STATES:
        key = prefix if state == "idle" else state + "_" + prefix
        rv[key] = Fixed(Transform(art(name, state, size), **placement), xfill=True, yfill=True)
    return rv
