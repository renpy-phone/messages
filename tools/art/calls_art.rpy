## Placeholder art for the Phone (calls) app.
##
## Icons are drawn at 2x their 1080p display size; frames at 1x, with the
## borders given to phone.art_frame() in calls_styles.rpy.

init -90 python in phone_art:

    CALLS_BOTH = ("light", "dark")

    def calls_lighter(color, amount=0.22):
        """`color` (#rrggbb) mixed with white."""
        r, g, b = (int(color[i:i + 2], 16) for i in (1, 3, 5))
        mix = lambda v: int(round(v + (255 - v) * amount))
        return "#{:02x}{:02x}{:02x}".format(mix(r), mix(g), mix(b))

    def calls_round(t, s, key, ch, size, glyph_scale=0.42):
        """A round button in theme color `key` with a white glyph."""
        fill = c(t, key)
        if s == "hover":
            fill = calls_lighter(fill)
        d = layers(size, size, circle(fill, size), glyph(ch, "#ffffff", size * glyph_scale))
        if s == "insensitive":
            d = Transform(d, alpha=0.4)
        return d

    # Home screen icon ------------------------------------------------------

    spec("apps/calls/icon", (144, 144), lambda t, s: layers(
        144, 144,
        rounded("#34c759" if s == "idle" else calls_lighter("#34c759", 0.15), 144, 144, 34),
        glyph("✆", "#ffffff", 72),
    ), ("idle", "hover"))

    # Round call buttons (up to 82 px on screen) --------------------------------

    CALLS_ROUND = 164
    spec("calls/accept", (CALLS_ROUND, CALLS_ROUND), lambda t, s: calls_round(t, s, "success", "✆", CALLS_ROUND),
         ("idle", "hover", "insensitive"), CALLS_BOTH)
    spec("calls/decline", (CALLS_ROUND, CALLS_ROUND), lambda t, s: calls_round(t, s, "danger", "✕", CALLS_ROUND),
         ("idle", "hover"), CALLS_BOTH)
    spec("calls/hangup", (CALLS_ROUND, CALLS_ROUND), lambda t, s: calls_round(t, s, "danger", "✕", CALLS_ROUND),
         ("idle", "hover", "insensitive"), CALLS_BOTH)
    spec("calls/message", (CALLS_ROUND, CALLS_ROUND), lambda t, s: calls_round(t, s, "accent", "❝", CALLS_ROUND),
         ("idle", "hover", "insensitive"), CALLS_BOTH)

    # Call button of a Contacts row (44 px) -------------------------------------

    def calls_row_call(t, s):
        if s == "hover":
            return layers(88, 88, circle(c(t, "success"), 88), glyph("✆", "#ffffff", 44))
        d = layers(88, 88, circle(c(t, "surface_alt"), 88),
                   glyph("✆", c(t, "subtext" if s == "insensitive" else "success"), 44))
        if s == "insensitive":
            d = Transform(d, alpha=0.5)
        return d

    spec("calls/row_call", (88, 88), calls_row_call, ("idle", "hover", "insensitive"), CALLS_BOTH)

    # Keypad (keys are 84 px, the delete key's icon 40 px) ------------------------

    spec("calls/key", (168, 168), lambda t, s: circle(c(t, "divider" if s == "hover" else "surface_alt"), 168),
         ("idle", "hover"), CALLS_BOTH)
    spec("calls/delete", (80, 80), lambda t, s: glyph("⌫", c(t, "text" if s == "hover" else "subtext"), 60),
         ("idle", "hover"), CALLS_BOTH)

    # Call direction icons for Recents (18 px) ----------------------------------

    for _calls_dir, _calls_ch, _calls_key in (
            ("incoming", "⬋", "subtext"),
            ("outgoing", "⬈", "subtext"),
            ("missed", "⬋", "danger"),
            ("declined", "⬋", "danger")):
        spec("calls/" + _calls_dir, (36, 36),
             (lambda ch, key: lambda t, s: glyph(ch, c(t, key), 32))(_calls_ch, _calls_key),
             themes=CALLS_BOTH)

    # Call screens (dark in both themes) ----------------------------------------

    # Pulsing ring behind the caller's avatar (150 px).
    spec("calls/pulse", (300, 300), lambda t, s: circle("#ffffff", 300))

    # Avatar of a caller who is not a contact (up to 150 px).
    spec("calls/unknown_caller", (300, 300), lambda t, s: layers(
        300, 300,
        circle("#8e8e93", 300),
        glyph("☏", "#ffffff", 150),
    ))

    # Frames --------------------------------------------------------------------

    # In-call pill: art_frame("calls/pill", 32).
    spec("calls/pill", (96, 96), lambda t, s: rounded(c(t, "call_bg"), 96, 96, 32))

    # Recent calls box on a contact card: art_frame("calls/card", 18).
    spec("calls/card", (64, 64), lambda t, s: rounded(c(t, "surface"), 64, 64, 18), themes=CALLS_BOTH)
