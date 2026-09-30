## Phone app styles.

init offset = -1

style phone_calls_dir_glyph is phone_glyph:
    size phone.text_px(16)
    yalign 0.5

style phone_calls_time is phone_subtext:
    size phone.text_px(16)
    yalign 0.5
    layout "nobreak"

style phone_calls_info is empty:
    xysize (phone.px(30), phone.px(40))

style phone_calls_info_text is phone_default:
    size phone.px(30)
    color phone.color("accent")
    hover_color phone.color("text")
    xalign 0.5
    yalign 0.5

style phone_calls_row_call is empty:
    xysize (phone.px(44), phone.px(44))
    background phone.circle("surface_alt", phone.px(44))
    hover_background phone.circle("success", phone.px(44))
    insensitive_background Transform(phone.circle("surface_alt", phone.px(44)), alpha=0.5)

style phone_calls_row_call_glyph is phone_glyph:
    size phone.px(22)
    color phone.color("success")
    hover_color "#ffffff"
    insensitive_color phone.color("subtext")
    xalign 0.5
    yalign 0.5

# Contact card ------------------------------------------------------------------

style phone_calls_card_name is phone_title:
    size phone.text_px(30)
    xalign 0.5
    text_align 0.5

style phone_calls_card_number is phone_subtext:
    size phone.text_px(20)
    xalign 0.5

style phone_calls_card_action is phone_default:
    size phone.text_px(17)
    color phone.color("accent")
    xalign 0.5

style phone_calls_section is phone_subtext:
    size phone.text_px(15)
    bold True
    xpos phone.px(24)

style phone_calls_card_list is empty:
    background phone.rounded("surface", "md")
    xfill True
    xmargin phone.px(16)
    padding (phone.px(16), phone.px(12))

style phone_calls_card_record is phone_default:
    size phone.text_px(18)
    xpos phone.px(28)
    yalign 0.5
    layout "nobreak"

# Keypad ------------------------------------------------------------------------

style phone_calls_dialed is phone_default:
    size phone.text_px(38)
    xalign 0.5
    layout "nobreak"

style phone_calls_dialed_name is phone_subtext:
    size phone.text_px(17)
    color phone.color("accent")
    xalign 0.5

style phone_calls_key is empty:
    xysize (phone.px(84), phone.px(84))
    background phone.circle("surface_alt", phone.px(84))
    hover_background phone.circle("divider", phone.px(84))

style phone_calls_key_digit is phone_default:
    size phone.px(34)
    xalign 0.5

style phone_calls_key_letters is phone_subtext:
    size phone.px(11)
    bold True
    xalign 0.5

style phone_calls_backspace is empty:
    xysize (phone.px(82), phone.px(82))

style phone_calls_backspace_text is phone_glyph:
    size phone.px(30)
    color phone.color("subtext")
    hover_color phone.color("text")
    xalign 0.5
    yalign 0.5

# Call screens ------------------------------------------------------------------

style phone_calls_caller_name is phone_default:
    size phone.text_px(34)
    color phone.color("call_text")
    xalign 0.5
    text_align 0.5
    xmaximum phone.px(400)

style phone_calls_status is phone_default:
    size phone.text_px(19)
    color phone.color("call_subtext")
    xalign 0.5
    text_align 0.5

style phone_calls_round is empty

style phone_calls_round_glyph is phone_glyph:
    color "#ffffff"
    xalign 0.5
    yalign 0.5

style phone_calls_round_label is phone_default:
    size phone.text_px(16)
    color phone.color("call_text")
    xalign 0.5

# In-call overlay ---------------------------------------------------------------

style phone_calls_pill is empty:
    background phone.rounded("call_bg", "lg")
    xalign 0.5
    ypos phone.px(18)
    padding (phone.px(10), phone.px(10))

style phone_calls_pill_name is phone_default:
    size phone.text_px(19)
    bold True
    color phone.color("call_text")
    layout "nobreak"

style phone_calls_active_timer is phone_default:
    size phone.text_px(16)
    color phone.color("success")
