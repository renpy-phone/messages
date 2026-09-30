## Placeholder art for the Settings app (gui/phone/settings/ and
## gui/phone/apps/settings/).

init -90 python in phone_art:
    from store import Color

    # Home screen icon: the old glyph on the old gray squircle.
    def settings_icon(t, s):
        color = "#8e8e93"
        if s == "hover":
            color = Color(color).tint(0.8).hexcode
        return layers(144, 144, rounded(color, 144, 144, 34), glyph("✱", "#ffffff", 72))

    spec("apps/settings/icon", (144, 144), settings_icon, ("idle", "hover"))

    # Text size segmented control: the track behind the segments, and one
    # segment (transparent when idle, accent when selected). 9-slice frames,
    # border 18.
    spec("settings/segmented", (64, 64), lambda t, s: rounded(c(t, "surface_alt"), 64, 64, 18), themes=BOTH)

    def settings_segment(t, s):
        if s == "idle":
            return Solid("#0000")
        if s == "hover":
            return rounded(c(t, "divider"), 64, 64, 18)
        color = c(t, "accent")
        if s == "selected_hover":
            color = Color(color).tint(0.85).hexcode
        return rounded(color, 64, 64, 18)

    spec("settings/segment", (64, 64), settings_segment,
         ("idle", "hover", "selected_idle", "selected_hover"), BOTH)

    # Mask that rounds the wallpaper thumbnail in the Wallpaper row. 9-slice,
    # border 8.
    spec("settings/thumbnail_mask", (32, 32), lambda t, s: rounded("#ffffff", 32, 32, 8))
