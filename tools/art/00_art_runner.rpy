## Renders every art spec to PHONE_RENDER_ART, then quits. Loaded only by
## tools/art/render_art.sh, never by the game.
##
## A spec names an art file and says how to draw it:
##
##     spec("nav/back", (72, 72), lambda t, s: glyph("‹", ink(t, s), 60),
##          states=("idle", "hover", "insensitive"), themes=("light", "dark"))
##
## The builder gets the theme name and state and returns a displayable of the
## given size. Light is written to gui/phone/<name>_<state>.png, other themes
## to gui/phone/themes/<theme>/<name>_<state>.png.

init -100 python in phone_art:
    import os
    import store
    from store import Fixed, Frame, Solid, Text, Transform, TintMatrix

    specs = []

    def spec(name, size, builder, states=("idle",), themes=("light",)):
        specs.append((name, size, builder, states, themes))

    # Files outside gui/phone/ (e.g. demo pictures), relative to game/.
    files = []

    def file_spec(path, size, builder):
        files.append((path, size, builder))

    # Drawing helpers ------------------------------------------------------

    SHAPES = "_art/shapes/"
    GLYPH_FONT = "DejaVuSans.ttf"

    def c(theme, key):
        """A color of `theme`, or `key` itself if it's already a color."""
        if key.startswith("#"):
            return key
        return store.phone.cfg.themes[theme][key]

    def tint(image, color):
        return Transform(image, matrixcolor=TintMatrix(color))

    def rounded(color, w, h, radius):
        """A w x h rounded rectangle with the given corner radius."""
        for fn, r in (("round_8.png", 8), ("round_18.png", 18), ("round_48.png", 48)):
            if radius <= r:
                break
        k = float(radius) / r
        frame = Transform(Frame(tint(SHAPES + fn, color), r, r), xysize=(int(round(w / k)), int(round(h / k))))
        return Transform(frame, zoom=k)

    def circle(color, size):
        return Transform(tint(SHAPES + "circle.png", color), xysize=(size, size))

    def glyph(ch, color, size, **kw):
        return Text(ch, font=GLYPH_FONT, size=int(size), color=color, xalign=0.5, yalign=0.5, **kw)

    def layers(w, h, *children):
        return Fixed(*children, xysize=(w, h))

label splashscreen:
    python:
        out = os.environ.get("PHONE_RENDER_ART")
        if out:
            only = os.environ.get("PHONE_RENDER_ONLY", "")
            count = 0
            for name, size, builder, states, themes in phone_art.specs:
                if only and not name.startswith(only):
                    continue
                for theme in themes:
                    folder = out if theme == "light" else os.path.join(out, "themes", theme)
                    for state in states:
                        path = os.path.join(folder, "{}_{}.png".format(name, state))
                        if not os.path.isdir(os.path.dirname(path)):
                            os.makedirs(os.path.dirname(path))
                        d = Fixed(builder(theme, state), xysize=size)
                        renpy.render_to_file(d, path, width=size[0], height=size[1])
                        count += 1
            game_dir = os.path.dirname(os.path.dirname(out.rstrip("/")))
            for path, size, builder in phone_art.files:
                if only and not path.startswith(only):
                    continue
                full = os.path.join(game_dir, path)
                if not os.path.isdir(os.path.dirname(full)):
                    os.makedirs(os.path.dirname(full))
                renpy.render_to_file(Fixed(builder(), xysize=size), full, width=size[0], height=size[1])
                count += 1
            print("ART DONE {} files".format(count))
            renpy.quit()
    return
