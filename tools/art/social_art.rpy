## Placeholder art for the Social app (game/gui/phone/social/ and
## apps/social/). Icons are drawn at 2x their 1080p display size, frames at
## 1x with borders in 1080p pixels (see social_styles.rpy).
##
## Outlines are drawn by stamping small anti-aliased circles along a path, so
## the icons need no source images. Every helper here starts with `social_`
## because all art spec files share the phone_art store.

init -90 python in phone_art:
    import math
    from store import absolute

    SOCIAL_THEMES = ("light", "dark")

    # The like color is only used by the art, so it lives here, not in the
    # theme.
    SOCIAL_LIKE = {"light": "#ed4956", "dark": "#ff3040"}

    def social_mix(a, b, t):
        """Hex color between a and b (t=0 is a, t=1 is b)."""
        a = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
        b = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
        return "#" + "".join("{:02x}".format(int(round(x + (y - x) * t))) for x, y in zip(a, b))

    # Paths ---------------------------------------------------------------

    def social_arc(cx, cy, r, a0, a1):
        """Points on a circle from angle a0 to a1 (radians, y down)."""
        n = max(2, int(abs(a1 - a0) * r / 0.5))
        return [(cx + r * math.cos(a0 + (a1 - a0) * i / float(n)), cy + r * math.sin(a0 + (a1 - a0) * i / float(n)))
                for i in range(n + 1)]

    def social_line(p, q):
        n = max(2, int(math.hypot(q[0] - p[0], q[1] - p[1]) / 0.5))
        return [(p[0] + (q[0] - p[0]) * i / float(n), p[1] + (q[1] - p[1]) * i / float(n)) for i in range(n + 1)]

    def social_tangent(cx, cy, r, px, py, side):
        """Angle of the point where a line from (px, py) touches the circle."""
        d = math.hypot(px - cx, py - cy)
        return math.atan2(py - cy, px - cx) + side * math.acos(r / d)

    def social_heart_path(cx, cy, s):
        """A heart centered on (cx, cy), `s` pixels per unit: two round lobes
        joined by straight sides to a point."""
        a, r, h = 0.62, 1.0, 2.1
        top, bottom = -r, h
        oy = cy - (top + bottom) / 2.0 * s
        lx, rx = cx - a * s, cx + a * s
        tip = (cx, oy + h * s)
        tr = social_tangent(rx, oy, r * s, tip[0], tip[1], -1)
        tl = math.pi - tr
        dip = math.atan2(-math.sqrt(r * r - a * a), -a)
        pts = social_line(tip, (rx + r * s * math.cos(tr), oy + r * s * math.sin(tr)))
        pts += social_arc(rx, oy, r * s, tr, dip - 2 * math.pi if dip > tr else dip)
        pts += social_arc(lx, oy, r * s, math.pi - dip, tl - 2 * math.pi if tl > math.pi - dip else tl)
        pts += social_line((lx + r * s * math.cos(tl), oy + r * s * math.sin(tl)), tip)
        return pts

    def social_bubble_path(cx, cy, r, tip_angle, tip_dist):
        """A round speech bubble whose tail comes to a point."""
        tip = (cx + tip_dist * math.cos(tip_angle), cy + tip_dist * math.sin(tip_angle))
        t0 = social_tangent(cx, cy, r, tip[0], tip[1], 1)
        t1 = social_tangent(cx, cy, r, tip[0], tip[1], -1)
        pts = social_line(tip, (cx + r * math.cos(t0), cy + r * math.sin(t0)))
        pts += social_arc(cx, cy, r, t0, t1 + 2 * math.pi)
        pts += social_line((cx + r * math.cos(t1), cy + r * math.sin(t1)), tip)
        return pts

    # Drawing -------------------------------------------------------------

    def social_stroke(points, width, color):
        """The path drawn with a round pen `width` pixels wide."""
        dot = circle("#ffffff", width)
        stamps = [Transform(dot, xpos=absolute(x - width / 2.0), ypos=absolute(y - width / 2.0), subpixel=True) for x, y in points]
        return tint(Fixed(*stamps), color)

    def social_fill(points, center, width, color):
        """The closed path filled, by stroking copies shrunk towards `center`."""
        cx, cy = center
        reach = max(math.hypot(x - cx, y - cy) for x, y in points)
        rings = int(math.ceil(reach / (width * 0.4)))
        stamps = []
        dot = circle("#ffffff", width)
        for i in range(rings + 1):
            k = 1.0 - i / float(rings)
            step = max(1, int(1.0 / max(k, 0.05)))
            for x, y in points[::step]:
                x, y = cx + (x - cx) * k, cy + (y - cy) * k
                stamps.append(Transform(dot, xpos=absolute(x - width / 2.0), ypos=absolute(y - width / 2.0), subpixel=True))
        return tint(Fixed(*stamps), color)

    # Feed icons (30px at 1080p) -------------------------------------------

    SOCIAL_ICON = 60
    SOCIAL_PEN = 5

    def social_heart(t, s):
        path = social_heart_path(30, 30, 14.5)
        if s.startswith("selected"):
            color = SOCIAL_LIKE[t]
            if s == "selected_hover":
                color = social_mix(color, c(t, "text"), 0.25)
            return social_fill(path, (30, 32), SOCIAL_PEN, color)
        return social_stroke(path, SOCIAL_PEN, c(t, "subtext" if s == "hover" else "text"))

    spec("social/like", (SOCIAL_ICON, SOCIAL_ICON), social_heart,
         ("idle", "hover", "selected_idle", "selected_hover"), SOCIAL_THEMES)

    spec("social/comment", (SOCIAL_ICON, SOCIAL_ICON),
         lambda t, s: social_stroke(social_bubble_path(31, 29, 21, math.radians(135), 28), SOCIAL_PEN,
                                    c(t, "subtext" if s == "hover" else "text")),
         ("idle", "hover"), SOCIAL_THEMES)

    # Ring around the player's avatar in the feed header (52px at 1080p).

    spec("social/profile_ring", (104, 104),
         lambda t, s: social_stroke(social_arc(52, 52, 49, 0, 2 * math.pi), 4, c(t, "accent" if s == "hover" else "divider")),
         ("idle", "hover"), SOCIAL_THEMES)

    # Button frames (1x, borders in 1080p pixels) ---------------------------

    # Follow / Following: border 8.
    def social_follow_fill(s):
        return {"hover": "text", "selected_idle": "surface_alt", "selected_hover": "divider"}.get(s, "accent")

    spec("social/follow_button", (32, 32), lambda t, s: rounded(c(t, social_follow_fill(s)), 32, 32, 8),
         ("idle", "hover", "selected_idle", "selected_hover"), SOCIAL_THEMES)

    # Comment options and "Load more": border 18.
    spec("social/option_button", (64, 64),
         lambda t, s: rounded(c(t, "accent" if s == "hover" else "surface_alt"), 64, 64, 18),
         ("idle", "hover"), SOCIAL_THEMES)

    # Home screen icon: a camera on the app's squircle.

    SOCIAL_APP_COLOR = "#c13584"

    def social_app_icon(t, s):
        back = SOCIAL_APP_COLOR if s == "idle" else social_mix(SOCIAL_APP_COLOR, "#ffffff", 0.18)
        return layers(
            144, 144,
            rounded(back, 144, 144, 34),
            Transform(rounded("#ffffff", 32, 18, 6), xpos=56, ypos=34),
            Transform(rounded("#ffffff", 88, 62, 14), xpos=28, ypos=44),
            Transform(circle(back, 40), xpos=52, ypos=55),
            Transform(circle("#ffffff", 24), xpos=60, ypos=63),
            Transform(circle(back, 8), xpos=98, ypos=52),
        )

    spec("apps/social/icon", (144, 144), social_app_icon, ("idle", "hover"))
