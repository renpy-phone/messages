# Framework styles. They run at init -1: after gui.init and phone.cfg
# overrides (both at init -2), and before game code at init 0, so a game can
# override any of them with its own `style phone_...:` statement.
#
# Shapes and icons come from art files under gui/phone/ (see phone.art_path);
# text colors and flat fills come from phone.color(), which reads the active
# theme. Changing the theme or text size calls gui.rebuild(), which re-runs
# these statements, so themed art (gui/phone/themes/<theme>/) is picked up.
#
# Frame borders below are in art pixels at 1080p scale.

init offset = -1

style phone_default:
    font (phone.cfg.font or getattr(gui, "text_font", "DejaVuSans.ttf"))
    size phone.text_px(22)
    color phone.color("text")
    outlines []
    antialias True

style phone_text is phone_default

style phone_glyph is phone_default:
    font phone.GLYPH_FONT

style phone_title is phone_default:
    size phone.text_px(26)
    bold True

style phone_subtext is phone_default:
    size phone.text_px(18)
    color phone.color("subtext")

# The device ------------------------------------------------------------------

style phone_device is empty:
    background phone.art_frame("device/frame", 48)
    padding (phone.px(phone.cfg.bezel), phone.px(phone.cfg.bezel))
    xysize (phone.px(phone.cfg.width), phone.px(phone.cfg.height))

style phone_display is empty:
    xysize phone.display_size()

style phone_content is empty:
    xysize phone.content_size()

style phone_status_bar is empty:
    xfill True
    ysize phone.px(phone.STATUS_HEIGHT)
    padding (phone.px(22), 0)

style phone_status_text is phone_default:
    size phone.px(17)
    bold True
    yalign 0.5

style phone_nav_bar is empty:
    xfill True
    ysize phone.px(phone.NAV_HEIGHT)

style phone_nav_button is empty:
    xysize (phone.px(90), phone.px(phone.NAV_HEIGHT))
    xalign 0.5
    yalign 0.5

# Home screen -----------------------------------------------------------------

style phone_home_clock is phone_default:
    size phone.px(72)
    color phone.color("status_text")
    xalign 0.5

style phone_app_button is empty:
    xsize phone.px(100)
    ysize phone.px(126)

style phone_app_label is phone_default:
    size phone.px(15)
    color phone.color("status_text")
    xalign 0.5
    text_align 0.5
    layout "nobreak"

# Shared components -----------------------------------------------------------

style phone_header is empty:
    background phone.color("surface")
    xfill True
    ysize phone.px(phone.HEADER_HEIGHT)
    padding (phone.px(12), 0)

style phone_header_title is phone_title:
    xalign 0.5
    yalign 0.5
    layout "nobreak"

style phone_header_button is empty:
    yalign 0.5
    padding (phone.px(10), phone.px(8))

style phone_header_button_text is phone_default:
    color phone.color("accent")
    hover_color phone.color("text")
    size phone.text_px(22)

style phone_header_back is phone_header_button:
    left_padding phone.px(28)

style phone_header_back_text is phone_header_button_text

style phone_body is empty:
    xfill True
    ysize phone.page_body_height()

style phone_row is empty:
    xfill True
    padding (phone.px(16), phone.px(12))
    background phone.color("surface")
    hover_background phone.color("surface_alt")

style phone_row_title is phone_default:
    bold True
    layout "nobreak"

style phone_row_subtext is phone_subtext:
    layout "nobreak"

style phone_divider is empty:
    xfill True
    ysize max(1, phone.px(1))
    background phone.color("divider")

style phone_badge is empty:
    background phone.art_frame("common/badge", 12)
    padding (phone.px(7), phone.px(1))
    xminimum phone.px(24)
    ysize phone.px(24)

style phone_badge_text is phone_default:
    size phone.px(15)
    bold True
    color phone.color("badge_text")
    xalign 0.5
    yalign 0.5

style phone_button is empty:
    background phone.art_frame("common/button", 18)
    hover_background phone.art_frame("common/button", 18, "hover")
    insensitive_background phone.art_frame("common/button", 18, "insensitive")
    padding (phone.px(20), phone.px(12))

style phone_button_text is phone_default:
    color phone.color("accent_text")
    insensitive_color phone.color("subtext")
    xalign 0.5
    text_align 0.5

style phone_tab is empty:
    padding (phone.px(8), phone.px(12))
    background None
    selected_background phone.color("surface_alt")

style phone_tab_text is phone_default:
    xalign 0.5
    size phone.text_px(19)
    color phone.color("subtext")
    hover_color phone.color("text")
    selected_color phone.color("accent")

style phone_vscrollbar is vscrollbar:
    xsize phone.px(4)
    base_bar Solid("#0000")
    thumb phone.art_frame("common/scrollbar", 2)
    unscrollable "hide"

style phone_empty_text is phone_subtext:
    xalign 0.5
    yalign 0.5
    text_align 0.5

# Notification banner and HUD button ------------------------------------------

style phone_notification is empty:
    background phone.art_frame("common/banner", 18)
    xalign 0.5
    ypos phone.px(20)
    xsize phone.px(440)
    padding (phone.px(16), phone.px(12))

style phone_hud_button is empty:
    xysize (phone.px(72), phone.px(72))

style phone_avatar_initial is phone_default:
    color "#ffffff"
    bold True


init python in phone:
    # Remember what the styles were built from, so lint can spot overrides
    # that came too late to affect them.
    _style_snapshot = _style_inputs()
