# Styles for the Wallpapers app. Built at init -1 like the framework styles,
# so games can override them with their own `style phone_wallpapers_...:`.

init offset = -1

style phone_wallpapers_grid is empty:
    xfill True
    spacing phone.px(22)

style phone_wallpapers_grid_row is empty:
    xalign 0.5
    spacing phone.px(24)

style phone_wallpapers_tile is empty:
    padding (0, 0)

style phone_wallpapers_tile_name is phone_default:
    size phone.text_px(18)
    xalign 0.5
    text_align 0.5
    layout "nobreak"

style phone_wallpapers_tile_name_current is phone_wallpapers_tile_name:
    color phone.color("accent")
    bold True

style phone_wallpapers_tile_clock is phone_default:
    size phone.px(30)
    color "#ffffff"
    xalign 0.5
    ypos phone.px(26)

style phone_wallpapers_check is phone_glyph:
    size phone.px(18)
    bold True
    color phone.color("accent_text")
    xalign 0.5
    yalign 0.5

style phone_wallpapers_new is empty:
    background phone.rounded("badge", "sm")
    padding (phone.px(9), phone.px(4))
    xalign 0.0
    yalign 1.0
    offset (phone.px(10), -phone.px(12))

style phone_wallpapers_new_text is phone_default:
    size phone.px(14)
    bold True
    color phone.color("badge_text")

style phone_wallpapers_preview_panel is empty:
    background "#00000080"
    xfill True
    yalign 1.0
    padding (phone.px(20), phone.px(18), phone.px(20), phone.px(22))

style phone_wallpapers_preview_name is phone_default:
    size phone.text_px(22)
    bold True
    color "#ffffff"
    xalign 0.5
    text_align 0.5

style phone_wallpapers_preview_note is phone_default:
    size phone.text_px(26)
    bold True
    color "#ffffff"

style phone_wallpapers_preview_hint is phone_default:
    size phone.text_px(18)
    color "#ffffffcc"
    xalign 0.5
    text_align 0.5
    xmaximum phone.px(320)

style phone_wallpapers_preview_set is phone_button:
    xminimum phone.px(200)
    insensitive_background Transform(phone.rounded("#ffffff", "md"), alpha=0.25)

style phone_wallpapers_preview_set_text is phone_button_text:
    bold True
    insensitive_color "#ffffff"

style phone_wallpapers_preview_cancel is phone_button:
    xminimum phone.px(140)
    background Transform(phone.rounded("#ffffff", "md"), alpha=0.22)
    hover_background Transform(phone.rounded("#ffffff", "md"), alpha=0.38)

style phone_wallpapers_preview_cancel_text is phone_button_text:
    color "#ffffff"
