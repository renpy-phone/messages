## Placeholder art for the Messages app (game/phone/apps/messages/).
##
## Icons are drawn at 2x their 1080p display size; frames at 1x, with the
## borders given next to each spec (pass the same borders to art_frame).

init -90 python in phone_art:
    from store import AlphaMask

    MESSAGES_THEMES = ("light", "dark")

    # Home screen icon ----------------------------------------------------

    def messages_icon(s):
        color = "#5dd47a" if s == "hover" else "#34c759"
        return layers(144, 144, rounded(color, 144, 144, 34), glyph("❝", "#ffffff", 72))

    spec("apps/messages/icon", (144, 144), lambda t, s: messages_icon(s), ("idle", "hover"))

    # Chat bubbles --------------------------------------------------------
    #
    # 72x64 frames, borders (26, 18, 18, 24) for incoming bubbles and
    # (18, 18, 26, 24) for outgoing ones. The body leaves an 8px gutter on
    # the sender's side, where the _tail variant (the last bubble of a run)
    # draws its tail, so both variants line up.

    def messages_bubble(color, tail):
        parts = [Transform(rounded(color, 64, 64, 18), xpos=8)]
        if tail:
            # A block under the bottom corner, hollowed into a hook by a
            # circle to its left.
            block = layers(72, 64, Transform(rounded(color, 30, 24, 4), xpos=0, ypos=40))
            carve = layers(72, 64, Transform(circle("#ffffff", 32), xpos=-24, ypos=24))
            parts.append(AlphaMask(block, carve, invert=True))
        return layers(72, 64, *parts)

    def messages_bubble_out(color, tail):
        return Transform(messages_bubble(color, tail), xzoom=-1.0)

    spec("messages/bubble_in", (72, 64), lambda t, s: messages_bubble(c(t, "bubble_in"), False), themes=MESSAGES_THEMES)
    spec("messages/bubble_in_tail", (72, 64), lambda t, s: messages_bubble(c(t, "bubble_in"), True), themes=MESSAGES_THEMES)
    spec("messages/bubble_out", (72, 64), lambda t, s: messages_bubble_out(c(t, "bubble_out"), False), themes=MESSAGES_THEMES)
    spec("messages/bubble_out_tail", (72, 64), lambda t, s: messages_bubble_out(c(t, "bubble_out"), True), themes=MESSAGES_THEMES)

    # Conversation header back button (40x40 at 1080p).
    spec("messages/back", (80, 80), lambda t, s: glyph("‹", c(t, "text" if s == "hover" else "accent"), 112, yoffset=-6),
         ("idle", "hover"), MESSAGES_THEMES)

    # Typing indicator: one dot, shown three times (10x10 at 1080p).
    spec("messages/typing_dot", (20, 20), lambda t, s: circle(c(t, "subtext"), 20), themes=MESSAGES_THEMES)

    # Reply panel -----------------------------------------------------------

    # Reply option button, border 18.
    spec("messages/reply", (64, 64), lambda t, s: rounded(c(t, "bubble_out" if s == "hover" else "surface_alt"), 64, 64, 18),
         ("idle", "hover"), MESSAGES_THEMES)

    # Idle composer bar, border 18.
    spec("messages/composer", (64, 64), lambda t, s: rounded(c(t, "surface_alt"), 64, 64, 18), themes=MESSAGES_THEMES)

    # Pictures --------------------------------------------------------------

    # Alpha masks that round the corners of picture thumbnails: border 18,
    # and border 8 for small ones (reply options).
    spec("messages/thumb_mask", (64, 64), lambda t, s: rounded("#ffffff", 64, 64, 18))
    spec("messages/thumb_mask_small", (32, 32), lambda t, s: rounded("#ffffff", 32, 32, 8))

    # Ring behind the second member of a group avatar (up to 48x48 at 1080p).
    spec("messages/group_ring", (96, 96), lambda t, s: circle(c(t, "surface"), 96), themes=MESSAGES_THEMES)
