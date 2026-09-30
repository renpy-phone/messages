## Placeholder art for the phone shell and shared components.
##
## Icons are drawn at 2x their 1080p display size so they stay sharp at
## higher resolutions; frames are drawn at 1x because their borders are
## measured in 1080p pixels (see styles.rpy).

init -90 python in phone_art:

    BOTH = ("light", "dark")

    # Device --------------------------------------------------------------

    spec("device/frame", (128, 128), lambda t, s: rounded(c(t, "bezel"), 128, 128, 48), themes=BOTH)

    # Status bar ----------------------------------------------------------

    def signal(color):
        bars = [Solid(color, xysize=(8, h), xpos=4 + i * 12, yalign=1.0) for i, h in enumerate((8, 14, 20, 26))]
        return layers(48, 32, *bars)

    def battery_outline(color, back):
        return layers(
            48, 32,
            Transform(rounded(color, 40, 24, 6), xpos=0, yalign=0.5),
            Transform(rounded(back, 34, 18, 4), xpos=3, yalign=0.5),
            Transform(rounded(color, 26, 12, 3), xpos=7, yalign=0.5),
            Transform(rounded(color, 4, 10, 2), xpos=42, yalign=0.5),
        )

    spec("status/signal", (48, 32), lambda t, s: signal(c(t, "text")), themes=BOTH)
    spec("status/battery", (48, 32), lambda t, s: battery_outline(c(t, "text"), c(t, "surface")), themes=BOTH)
    spec("status/wallpaper/signal", (48, 32), lambda t, s: signal(c(t, "status_text")))
    spec("status/wallpaper/battery", (48, 32), lambda t, s: layers(
        48, 32,
        Transform(rounded(c(t, "status_text"), 40, 24, 6), xpos=0, yalign=0.5, alpha=0.45),
        Transform(rounded(c(t, "status_text"), 26, 12, 3), xpos=7, yalign=0.5),
        Transform(rounded(c(t, "status_text"), 4, 10, 2), xpos=42, yalign=0.5, alpha=0.45),
    ))

    # Navigation bar ------------------------------------------------------

    def nav_ink(t, s):
        return c(t, {"hover": "accent", "insensitive": "divider"}.get(s, "subtext"))

    NAV_STATES = ("idle", "hover", "insensitive")
    spec("nav/back", (72, 72), lambda t, s: glyph("‹", nav_ink(t, s), 64), NAV_STATES, BOTH)
    spec("nav/home", (72, 72), lambda t, s: glyph("○", nav_ink(t, s), 52), NAV_STATES, BOTH)
    spec("nav/close", (72, 72), lambda t, s: glyph("✕", nav_ink(t, s), 50), NAV_STATES, BOTH)

    # Floating phone button -----------------------------------------------

    spec("hud/button", (144, 144), lambda t, s: layers(
        144, 144,
        circle(c(t, "accent" if s == "hover" else "bezel"), 144),
        glyph("☏", "#ffffff", 68),
    ), ("idle", "hover"))

    # Shared components ---------------------------------------------------

    spec("common/badge", (40, 24), lambda t, s: rounded(c(t, "badge"), 40, 24, 12))

    def button_fill(s):
        return {"hover": "text", "insensitive": "surface_alt"}.get(s, "accent")

    spec("common/button", (64, 64), lambda t, s: rounded(c(t, button_fill(s)), 64, 64, 18),
         ("idle", "hover", "insensitive"), BOTH)

    spec("common/banner", (64, 64), lambda t, s: rounded(c(t, "surface"), 64, 64, 18), themes=BOTH)

    spec("common/scrollbar", (8, 16), lambda t, s: rounded(c(t, "subtext"), 8, 16, 4), themes=BOTH)

    spec("common/back", (48, 48), lambda t, s: glyph("‹", c(t, "text" if s == "hover" else "accent"), 52, yoffset=-3),
         ("idle", "hover"), BOTH)

    spec("common/chevron", (48, 48), lambda t, s: glyph("›", c(t, "subtext"), 44), themes=BOTH)

    def toggle(t, on):
        return layers(
            104, 64,
            rounded(c(t, "success" if on else "divider"), 104, 64, 32),
            Transform(circle("#ffffff", 56), xpos=(44 if on else 4), yalign=0.5),
        )

    spec("common/toggle", (104, 64), lambda t, s: toggle(t, s.startswith("selected")),
         ("idle", "selected_idle"), BOTH)

    spec("common/avatar_mask", (256, 256), lambda t, s: circle("#ffffff", 256))
    spec("common/avatar_default", (256, 256), lambda t, s: circle("#8e8e93", 256))

    spec("common/check", (60, 60), lambda t, s: layers(60, 60, circle(c(t, "accent"), 60), glyph("✓", "#ffffff", 36)))
