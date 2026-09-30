# Styles of the Messages app. Built at init -1 like the framework styles, so a
# game can override any of them with its own `style phone_messages_...:`.
#
# Shapes come from art under gui/phone/messages/ (see tools/art/messages_art.rpy);
# frame borders below are in art pixels at 1080p scale.

init offset = -1

# Conversation header ---------------------------------------------------------

style phone_messages_header is phone_header:
    padding (phone.px(4), 0, phone.px(16), 0)

style phone_messages_back is empty:
    yalign 0.5
    padding (phone.px(2), phone.px(4))

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

# Bubble art leaves an 8px gutter on the sender's side for the tail, which
# the last bubble of a run (the _tail styles) draws.
style phone_messages_bubble_in is empty:
    background phone.art_frame("messages/bubble_in", (26, 18, 18, 24))
    padding (phone.px(24), phone.px(10), phone.px(16), phone.px(10))
    xmaximum int(phone.content_size()[0] * 0.72) + phone.px(8)
    xalign 0.0

style phone_messages_bubble_in_tail is phone_messages_bubble_in:
    background phone.art_frame("messages/bubble_in_tail", (26, 18, 18, 24))

style phone_messages_bubble_out is phone_messages_bubble_in:
    background phone.art_frame("messages/bubble_out", (18, 18, 26, 24))
    padding (phone.px(16), phone.px(10), phone.px(24), phone.px(10))
    xalign 1.0

style phone_messages_bubble_out_tail is phone_messages_bubble_out:
    background phone.art_frame("messages/bubble_out_tail", (18, 18, 26, 24))

style phone_messages_bubble_image is empty:
    padding (0, 0)

style phone_messages_bubble_in_text is phone_default:
    size phone.text_px(20)
    color phone.color("bubble_in_text")

style phone_messages_bubble_out_text is phone_messages_bubble_in_text:
    color phone.color("bubble_out_text")

style phone_messages_typing is empty:
    spacing phone.px(5)
    ysize phone.text_px(24)

# Reply panel and composer -----------------------------------------------------

style phone_messages_panel is empty:
    background phone.color("surface")
    xfill True
    padding (phone.px(14), phone.px(12))

style phone_messages_panel_label is phone_subtext:
    size phone.text_px(14)
    xalign 0.5

style phone_messages_reply is empty:
    background phone.art_frame("messages/reply", 18)
    hover_background phone.art_frame("messages/reply", 18, "hover")
    xfill True
    padding (phone.px(16), phone.px(11))

style phone_messages_reply_text is phone_default:
    size phone.text_px(19)
    color phone.color("accent")
    hover_color phone.color("bubble_out_text")
    xalign 0.5
    text_align 0.5

style phone_messages_composer is empty:
    background phone.art_frame("messages/composer", 18)
    xfill True
    padding (phone.px(16), phone.px(10))

style phone_messages_composer_text is phone_subtext:
    size phone.text_px(18)

style phone_messages_vscrollbar is phone_vscrollbar
