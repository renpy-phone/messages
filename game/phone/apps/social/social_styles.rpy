# Styles for the Social app. Like the framework styles, they are rebuilt when
# the theme or text size changes, and games may override any of them.

init offset = -1

style phone_social_logo is phone_title:
    size phone.text_px(30)
    yalign 0.5
    layout "nobreak"

style phone_social_header_button is empty:
    yalign 0.5
    padding (phone.px(6), phone.px(6))

style phone_social_card is empty:
    xfill True
    background phone.color("surface")
    padding (0, 0, 0, phone.px(16))

style phone_social_author is empty:
    xfill True
    padding (phone.px(14), phone.px(10))
    background None
    hover_background phone.color("surface_alt")

style phone_social_handle is phone_default:
    size phone.text_px(19)
    bold True
    layout "nobreak"

style phone_social_name is phone_subtext:
    size phone.text_px(16)
    layout "nobreak"

style phone_social_text is phone_default:
    size phone.text_px(19)

style phone_social_meta is phone_subtext:
    size phone.text_px(15)

style phone_social_link is empty:
    padding (0, phone.px(2))

style phone_social_link_text is phone_subtext:
    size phone.text_px(18)
    hover_color phone.color("text")

style phone_social_icon_button is empty:
    padding (phone.px(6), phone.px(6))

style phone_social_count is phone_default:
    size phone.text_px(22)
    bold True
    xalign 0.5
    text_align 0.5

style phone_social_count_label is phone_subtext:
    size phone.text_px(15)
    xalign 0.5
    text_align 0.5
    layout "nobreak"

style phone_social_follow_button is empty:
    background phone.rounded("accent", "sm")
    hover_background phone.rounded("text", "sm")
    selected_background phone.rounded("surface_alt", "sm")
    selected_hover_background phone.rounded("divider", "sm")
    padding (phone.px(12), phone.px(9))

style phone_social_follow_button_text is phone_default:
    size phone.text_px(18)
    bold True
    xalign 0.5
    text_align 0.5
    color phone.color("accent_text")
    hover_color phone.color("surface")
    selected_color phone.color("text")
    selected_hover_color phone.color("text")

style phone_social_option_button is empty:
    xfill True
    background phone.rounded("surface_alt", "md")
    hover_background phone.rounded("accent", "md")
    padding (phone.px(16), phone.px(12))

style phone_social_option_button_text is phone_default:
    size phone.text_px(18)
    hover_color phone.color("accent_text")

style phone_social_section is phone_subtext:
    size phone.text_px(15)
    bold True

style phone_social_tile is empty:
    background phone.color("surface_alt")

style phone_social_reply_panel is empty:
    xfill True
    background phone.color("surface")
    padding (phone.px(14), phone.px(10), phone.px(14), phone.px(12))
