"""renpy
init -980 python in phone:
"""

# Static configuration. Games change it from an init -2 block, so the values
# are in place before the phone styles are built at init -1:
#
#     init -2 python in phone:
#         cfg.player_name = "Sam"
#         cfg.themes["light"]["accent"] = "#e91e63"
#
# None of this is saved; it is rebuilt from the scripts every launch.


class PhoneConfig(python_object):
    def __init__(self):
        # Layout. The phone is authored at 1080p and scaled to the game's
        # resolution; `zoom` fine-tunes the size on top of that.
        self.zoom = 1.0
        self.xalign = 0.5
        self.yalign = 0.5
        self.layer = "screens"
        self.zorder = 100
        self.width = 470  # device size in 1080p pixels, bezel included
        self.height = 960
        self.bezel = 14

        # Behaviour.
        self.dim_background = "#0009"
        self.close_on_background_click = True
        self.hud = True  # floating phone button while the phone is closed
        self.hud_xalign = 0.98
        self.hud_yalign = 0.04
        self.home_columns = 4
        self.app_order = None  # list of app ids, or None to sort by App.order
        self.clock_format = "%H:%M"

        # Banners shown when something arrives while the phone is closed.
        self.notifications = True
        self.notification_duration = 3.0

        # Sounds played on the `channel`. None disables a sound.
        self.channel = "sound"
        self.sounds = {
            "message": None,
            "notification": None,
            "ringtone": None,
            "tap": None,
        }

        # The player.
        self.player_name = "You"
        self.player_handle = "you"
        self.player_avatar = None

        # Look.
        self.font = None  # None keeps the game's default font
        self.default_theme = "light"
        self.themes = {
            "light": {
                "bezel": "#111114",
                "bg": "#f2f2f7",
                "surface": "#ffffff",
                "surface_alt": "#e5e5ea",
                "text": "#111111",
                "subtext": "#6c6c72",
                "divider": "#d9d9de",
                "accent": "#0a84ff",
                "accent_text": "#ffffff",
                "badge": "#ff3b30",
                "badge_text": "#ffffff",
                "success": "#34c759",
                "danger": "#ff3b30",
                "status_text": "#ffffff",
                "scrim": "#00000066",
                "wallpaper": "#3d5a80",
                "bubble_in": "#e5e5ea",
                "bubble_in_text": "#111111",
                "bubble_out": "#0a84ff",
                "bubble_out_text": "#ffffff",
            },
            "dark": {
                "bezel": "#000000",
                "bg": "#000000",
                "surface": "#1c1c1e",
                "surface_alt": "#2c2c2e",
                "text": "#f5f5f7",
                "subtext": "#9a9aa0",
                "divider": "#38383a",
                "accent": "#0a84ff",
                "accent_text": "#ffffff",
                "badge": "#ff453a",
                "badge_text": "#ffffff",
                "success": "#30d158",
                "danger": "#ff453a",
                "status_text": "#ffffff",
                "scrim": "#00000099",
                "wallpaper": "#1b263b",
                "bubble_in": "#2c2c2e",
                "bubble_in_text": "#f5f5f7",
                "bubble_out": "#0a84ff",
                "bubble_out_text": "#ffffff",
            },
        }

        # Wallpapers the player can pick: list of (id, displayable, name).
        # The Wallpapers app reads this; games append to it.
        self.wallpapers = []
        self.default_wallpaper = None  # wallpaper id, or None for the theme color


cfg = PhoneConfig()


def _style_inputs():
    """The configuration the framework styles are computed from."""
    return repr((
        cfg.width, cfg.height, cfg.bezel, cfg.font, cfg.default_theme,
        sorted((k, sorted(v.items())) for k, v in cfg.themes.items()),
    ))
