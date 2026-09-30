# Styles of the Messages app. Built at init -1 like the framework styles, so a
# game can override any of them with its own `style phone_messages_...:`.

init offset = -1

# Conversation header ---------------------------------------------------------

style phone_messages_header is phone_header:
    padding (phone.px(4), 0, phone.px(16), 0)

style phone_messages_back is empty:
    yalign 0.5
    padding (phone.px(10), phone.px(4))

style phone_messages_back_text is phone_glyph:
    size phone.px(56)
    color phone.color("accent")
    hover_color phone.color("text")
    yalign 0.5

style phone_messages_title is phone_default:
    size phone.text_px(21)
    bold True
    layout "nobreak"

style phone_messages_subtitle is phone_subtext:
    size phone.text_px(15)
    layout "nobreak"

# Log --------------------------------------------------------------------------

style phone_messages_log is empty:
    xfill True
    spacing phone.px(6)

style phone_messages_note is phone_subtext:
    size phone.text_px(15)
    xalign 0.5
    text_align 0.5
    xmaximum int(phone.content_size()[0] * 0.8)

style phone_messages_sender is phone_subtext:
    size phone.text_px(14)
    layout "nobreak"

style phone_messages_bubble_in is empty:
    background phone.rounded("bubble_in", "md")
    padding (phone.px(16), phone.px(10))
    xmaximum int(phone.content_size()[0] * 0.72)
    xalign 0.0

style phone_messages_bubble_out is phone_messages_bubble_in:
    background phone.rounded("bubble_out", "md")
    xalign 1.0

style phone_messages_bubble_image is empty:
    padding (0, 0)

style phone_messages_bubble_in_text is phone_default:
    size phone.text_px(20)
    color phone.color("bubble_in_text")

style phone_messages_bubble_out_text is phone_messages_bubble_in_text:
    color phone.color("bubble_out_text")

style phone_messages_typing_text is phone_glyph:
    size phone.px(18)
    color phone.color("subtext")

# Reply panel and composer -----------------------------------------------------

style phone_messages_panel is empty:
    background phone.color("surface")
    xfill True
    padding (phone.px(14), phone.px(12))

style phone_messages_panel_label is phone_subtext:
    size phone.text_px(14)
    xalign 0.5

style phone_messages_reply is empty:
    background phone.rounded("surface_alt", "md")
    hover_background phone.rounded("bubble_out", "md")
    xfill True
    padding (phone.px(16), phone.px(11))

style phone_messages_reply_text is phone_default:
    size phone.text_px(19)
    color phone.color("accent")
    hover_color phone.color("bubble_out_text")
    xalign 0.5
    text_align 0.5

style phone_messages_composer is empty:
    background phone.rounded("surface_alt", "md")
    xfill True
    padding (phone.px(16), phone.px(10))

style phone_messages_composer_text is phone_subtext:
    size phone.text_px(18)

style phone_messages_vscrollbar is phone_vscrollbar
