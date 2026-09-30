# Styles for the Settings app.

init offset = -1

style phone_settings_section is empty:
    xfill True
    padding (phone.px(16), phone.px(22), phone.px(16), phone.px(8))

style phone_settings_section_text is phone_subtext:
    size phone.text_px(16)
    bold True

style phone_settings_item is empty:
    xfill True
    padding (phone.px(16), phone.px(12))
    background phone.color("surface")

style phone_settings_info_label is phone_default:
    yalign 0.5

style phone_settings_info_value is phone_subtext:
    size phone.text_px(20)
    xalign 1.0
    yalign 0.5
    text_align 1.0
    layout "nobreak"

style phone_segmented is empty:
    background phone.rounded("surface_alt", "md")
    padding (phone.px(3), phone.px(3))
    xfill True

style phone_segmented_button is empty:
    padding (phone.px(6), phone.px(8))
    selected_background phone.rounded("accent", "md")
    hover_background phone.rounded("divider", "md")
    selected_hover_background phone.rounded("accent", "md")

style phone_segmented_button_text is phone_default:
    size phone.text_px(18)
    xalign 0.5
    text_align 0.5
    layout "nobreak"
    color phone.color("text")
    selected_color phone.color("accent_text")
    bold True

style phone_settings_chevron is phone_glyph:
    size phone.text_px(30)
    color phone.color("subtext")
    yalign 0.5
