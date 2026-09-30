## Placeholder art for the Wallpapers app (gui/phone/wallpapers/ and
## gui/phone/apps/wallpapers/), including the six built-in wallpapers.

init -90 python in phone_art:
    import random
    from store import Color, Matrix

    # Home screen icon: the old glyph on the old orange squircle.
    def wallpapers_icon(t, s):
        color = "#ff9500"
        if s == "hover":
            color = Color(color).tint(0.8).hexcode
        return layers(144, 144, rounded(color, 144, 144, 34), glyph("◐", "#ffffff", 72))

    spec("apps/wallpapers/icon", (144, 144), wallpapers_icon, ("idle", "hover"))

    # Grid tile ------------------------------------------------------------

    # The outline drawn 4px around a thumbnail: faint when idle, accent when
    # the wallpaper is the current one. 9-slice, border 22 (the thumbnail's
    # 18px corner radius plus the 4px outline).
    def wallpapers_tile(t, s):
        if s == "idle":
            return Transform(rounded(c(t, "divider"), 64, 64, 22), alpha=0.6)
        if s == "hover":
            return Transform(rounded(c(t, "accent"), 64, 64, 22), alpha=0.5)
        color = c(t, "accent")
        if s == "selected_hover":
            color = Color(color).tint(0.8).hexcode
        return rounded(color, 64, 64, 22)

    spec("wallpapers/tile", (64, 64), wallpapers_tile,
         ("idle", "hover", "selected_idle", "selected_hover"), BOTH)

    # Mask that rounds a thumbnail. 9-slice, border 18.
    spec("wallpapers/mask", (64, 64), lambda t, s: rounded("#ffffff", 64, 64, 18))

    # A white padlock, shown on locked tiles (40px) and previews (64px).
    # Turns a white-on-black drawing into white on transparent, to cut the
    # shackle's hole.
    WALLPAPERS_BLACK_TO_CLEAR = Matrix([1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0])

    def wallpapers_lock(size):
        t = int(round(size * 0.12))  # stroke
        sw = int(round(size * 0.56))  # shackle width
        sx = (size - sw) // 2
        bw = int(round(size * 0.8))  # body
        bh = int(round(size * 0.5))
        by = size - bh
        arch = Transform(
            Fixed(
                circle("#ffffff", sw),
                Transform(circle("#000000", sw - 2 * t), align=(0.5, 0.5)),
                xysize=(sw, sw),
            ),
            mesh=True, matrixcolor=WALLPAPERS_BLACK_TO_CLEAR, crop=(0, 0, sw, sw // 2),
        )
        legs = by - sw // 2 + t
        return layers(
            size, size,
            Transform(arch, xpos=sx, ypos=0),
            Solid("#ffffff", xysize=(t, legs), xpos=sx, ypos=sw // 2),
            Solid("#ffffff", xysize=(t, legs), xpos=sx + sw - t, ypos=sw // 2),
            Transform(rounded("#ffffff", bw, bh, 20), xpos=(size - bw) // 2, ypos=by),
        )

    spec("wallpapers/lock", (128, 128), lambda t, s: wallpapers_lock(128))

    # Preview buttons (on the dark translucent panel). 9-slice, border 18.
    def wallpapers_set_button(t, s):
        if s == "insensitive":  # "Current"
            return Transform(rounded("#ffffff", 64, 64, 18), alpha=0.25)
        color = c(t, "accent")
        if s == "hover":
            color = Color(color).tint(0.8).hexcode
        return rounded(color, 64, 64, 18)

    spec("wallpapers/set_button", (64, 64), wallpapers_set_button, ("idle", "hover", "insensitive"), BOTH)

    spec("wallpapers/cancel_button", (64, 64),
         lambda t, s: Transform(rounded("#ffffff", 64, 64, 18), alpha=(0.38 if s == "hover" else 0.22)),
         ("idle", "hover"))

    # Built-in wallpapers --------------------------------------------------
    #
    # Pictures in the display's shape (540x1140 at 1080p), drawn at 900x1900
    # so they stay sharp at 1440p. The shapes are laid out on a 540x1140
    # canvas and scaled up.

    WALLPAPERS_SIZE = (900, 1900)
    WALLPAPERS_CANVAS = (540, 1140)

    def wallpapers_gradient(colors):
        """A smooth vertical gradient through `colors`, top to bottom."""
        w, h = WALLPAPERS_SIZE
        colors = [Color(x) for x in colors]
        steps = h // 2
        band = h / float(steps)
        children = []
        for i in range(steps):
            f = (i + 0.5) / steps * (len(colors) - 1)
            k = min(int(f), len(colors) - 2)
            col = colors[k].interpolate(colors[k + 1], f - k)
            y0 = int(round(i * band))
            y1 = int(round((i + 1) * band))
            children.append(Solid(col, xysize=(w, y1 - y0 + 1), ypos=y0))
        return Fixed(*children, xysize=(w, h))

    def wallpapers_shape(image, color, size, x, y, alpha=1.0):
        """A tinted white shape centered on (x, y) of the canvas."""
        return Transform(
            tint(SHAPES + image, color), xysize=(size, size),
            alpha=alpha, xpos=x, ypos=y, xanchor=0.5, yanchor=0.5,
        )

    def wallpapers_picture(colors, *shapes):
        w, h = WALLPAPERS_SIZE
        cw, ch = WALLPAPERS_CANVAS
        canvas = Transform(Fixed(*shapes, xysize=(cw, ch)), crop=(0, 0, cw, ch))
        return Transform(
            Fixed(wallpapers_gradient(colors), Transform(canvas, zoom=w / float(cw)), xysize=(w, h)),
            crop=(0, 0, w, h),
        )

    def wallpapers_night():
        cw, ch = WALLPAPERS_CANVAS
        rng = random.Random(7)
        stars = []
        for _i in range(34):
            size = rng.choice((4, 5, 6, 8))
            stars.append(wallpapers_shape("circle.png", "#ffffff", size, rng.randint(10, cw - 10), rng.randint(10, int(ch * 0.7)), rng.uniform(0.35, 0.9)))
        return wallpapers_picture(
            ["#070b1d", "#16224a", "#34467f"],
            *(stars + [
                wallpapers_shape("circle.png", "#f6f1d5", 150, 385, 330),
                wallpapers_shape("circle.png", "#101838", 132, 420, 310),
                wallpapers_shape("circle.png", "#0d1530", 900, 100, 1500),
                wallpapers_shape("circle.png", "#111b3b", 900, 520, 1560),
            ])
        )

    WALLPAPERS_BUILTIN = {
        "aurora": lambda: wallpapers_picture(
            ["#0f2027", "#203a43", "#2c5364"],
            wallpapers_shape("circle.png", "#43cea2", 560, 60, 330, 0.28),
            wallpapers_shape("circle.png", "#185a9d", 680, 470, 720, 0.35),
            wallpapers_shape("circle.png", "#7f7fd5", 360, 420, 180, 0.18),
        ),
        "dusk": lambda: wallpapers_picture(
            ["#1a1a40", "#6a2c70", "#e3646b", "#f9b17a"],
            wallpapers_shape("circle.png", "#ffe29a", 250, 270, 790, 0.95),
            wallpapers_shape("circle.png", "#3b1f4a", 1100, 30, 1400),
            wallpapers_shape("circle.png", "#2a1537", 1000, 560, 1440),
        ),
        "night": wallpapers_night,
        "lagoon": lambda: wallpapers_picture(
            ["#0b6e70", "#139a86", "#2bb884"],
            wallpapers_shape("ring.png", "#ffffff", 420, 470, 250, 0.22),
            wallpapers_shape("ring.png", "#ffffff", 260, 470, 250, 0.16),
            wallpapers_shape("ring.png", "#ffffff", 600, 60, 900, 0.18),
            wallpapers_shape("circle.png", "#ffffff", 180, 90, 520, 0.08),
        ),
        "coral": lambda: wallpapers_picture(
            ["#c0265f", "#e8566a", "#f98f6f"],
            wallpapers_shape("circle.png", "#ffffff", 520, 470, 180, 0.12),
            wallpapers_shape("circle.png", "#ffffff", 400, 40, 620, 0.10),
            wallpapers_shape("circle.png", "#ffd3a5", 420, 520, 1040, 0.25),
        ),
        "graphite": lambda: wallpapers_picture(
            ["#1c1d20", "#2c2e33", "#3d4046"],
            *[wallpapers_shape("ring.png", "#ffffff", s, 540, 1140, 0.07) for s in (300, 520, 740, 960, 1180, 1400)]
        ),
    }

    for _wid, _builder in WALLPAPERS_BUILTIN.items():
        file_spec("gui/phone/wallpapers/{}.png".format(_wid), WALLPAPERS_SIZE, _builder)
