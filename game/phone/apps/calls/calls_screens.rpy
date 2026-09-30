## Phone app screens.

transform phone_calls_pulse(delay=0.0):
    alpha 0.0 zoom 1.0
    pause delay
    block:
        alpha 0.5 zoom 1.0
        easeout 1.6 alpha 0.0 zoom 1.5
        repeat

transform phone_calls_bob:
    yoffset 0
    block:
        ease 0.7 yoffset -phone.px(8)
        ease 0.7 yoffset 0
        repeat


## The app: Recents, Contacts and Keypad tabs.
screen phone_calls(tab="recents"):
    if phone.calls_state.ringing is not None:
        # Reached with the nav bar's Back button while the phone rings.
        use phone_calls_incoming(phone.calls_state.ringing, phone.calls_state.ringing_can_decline)
    else:
        $ titles = {"recents": _("Recents"), "contacts": _("Contacts"), "keypad": _("Keypad")}
        side "t c b":
            xysize phone.content_size()

            vbox:
                if tab == "recents" and phone.calls_state.log:
                    use phone_header(titles[tab], back=False, right_text=_("Clear"), right_action=phone.ClearCallLog())
                else:
                    use phone_header(titles.get(tab, titles["recents"]), back=False)

            fixed:
                if tab == "contacts":
                    use phone_calls_contacts
                elif tab == "keypad":
                    use phone_calls_keypad
                else:
                    use phone_calls_recents

            vbox:
                use phone_divider
                use phone_tabs([
                    (_("Recents"), phone.CallsTab("recents"), tab not in ("contacts", "keypad")),
                    (_("Contacts"), phone.CallsTab("contacts"), tab == "contacts"),
                    (_("Keypad"), phone.CallsTab("keypad"), tab == "keypad"),
                    ])


screen phone_calls_recents():
    $ records = phone.call_log()

    # Missed calls count as seen once Recents is on screen.
    if phone.calls_state.unseen_missed:
        timer 0.1 action phone.CallsSeen()

    if not records:
        use phone_empty(_("No recent calls"))
    else:
        use phone_list:
            for rec in records:
                use phone_calls_log_row(rec)


screen phone_calls_log_row(rec):
    $ is_contact = phone.is_contact_key(rec.who)
    $ tint = phone.color("danger") if rec.direction == "missed" else phone.color("text")

    button:
        style "phone_row"
        action phone.CallContact(rec.who)
        alt phone.caller_name(rec.who)

        hbox:
            spacing phone.px(14)

            add phone.caller_avatar(rec.who, phone.px(48)) yalign 0.5

            vbox:
                yalign 0.5
                xsize phone.px(236)
                text phone.caller_name(rec.who) style "phone_row_title" color tint substitute False
                hbox:
                    spacing phone.px(6)
                    text phone.call_glyph(rec.direction):
                        style "phone_calls_dir_glyph"
                        color (phone.color("danger") if rec.direction in ("missed", "declined") else phone.color("subtext"))
                    text phone.call_description(rec) style "phone_row_subtext" substitute False

            fixed:
                xsize phone.px(96)
                ysize phone.px(48)
                yalign 0.5
                text (rec.time or ""):
                    style "phone_calls_time"
                    xalign 1.0
                    xoffset -phone.px(34)
                    substitute False
                if is_contact:
                    textbutton "›":
                        style "phone_calls_info"
                        xalign 1.0
                        yalign 0.5
                        action phone.Navigate("phone_calls_contact", who=rec.who)
                        alt _("Contact details")

    use phone_divider


screen phone_calls_contacts():
    $ people = phone.call_contacts()

    if not people:
        use phone_empty(_("No contacts"))
    else:
        use phone_list:
            for c in people:
                button:
                    style "phone_row"
                    action phone.Navigate("phone_calls_contact", who=c.id)

                    hbox:
                        spacing phone.px(14)
                        add phone.avatar(c.id, phone.px(48)) yalign 0.5
                        vbox:
                            yalign 0.5
                            xsize phone.px(286)
                            text c.name style "phone_row_title" substitute False
                            text (c.number or _("No number")) style "phone_row_subtext" substitute False
                        button:
                            style "phone_calls_row_call"
                            yalign 0.5
                            action phone.CallContact(c.id)
                            alt _("Call")
                            text "✆" style "phone_calls_row_call_glyph"

                use phone_divider


## Contact card with Call and Message buttons.
screen phone_calls_contact(who):
    $ c = phone.contact(who)
    $ records = phone.call_log(who)[:6]

    use phone_page(c.name):
        viewport:
            mousewheel True
            draggable True
            scrollbars "vertical"
            yfill True

            vbox:
                xfill True
                spacing phone.px(10)

                null height phone.px(28)
                add phone.avatar(who, phone.px(128)) xalign 0.5
                null height phone.px(4)
                text c.name style "phone_calls_card_name" substitute False
                text (c.number or _("No number")) style "phone_calls_card_number" substitute False
                null height phone.px(12)

                hbox:
                    xalign 0.5
                    spacing phone.px(56)
                    use phone_calls_round_button("✆", "success", _("Call"), phone.CallContact(who), size=68, label_style="phone_calls_card_action")
                    if phone.get_app("messages") is not None:
                        use phone_calls_round_button("❝", "accent", _("Message"), phone.Launch("messages", "phone_messages_thread", thread=who), size=68, label_style="phone_calls_card_action")

                if records:
                    null height phone.px(20)
                    text _("Recent calls") style "phone_calls_section"
                    frame:
                        style "phone_calls_card_list"
                        vbox:
                            for rec in records:
                                fixed:
                                    xfill True
                                    ysize phone.text_px(34)
                                    text phone.call_glyph(rec.direction):
                                        style "phone_calls_dir_glyph"
                                        color (phone.color("danger") if rec.direction in ("missed", "declined") else phone.color("subtext"))
                                    text phone.call_description(rec):
                                        style "phone_calls_card_record"
                                        color (phone.color("danger") if rec.direction == "missed" else phone.color("text"))
                                        substitute False
                                    text (rec.time or "") style "phone_calls_time" xalign 1.0 substitute False


## Dial pad.
screen phone_calls_keypad():
    $ dialed = phone.calls_state.dialed
    $ match = phone.contact_by_number(dialed)

    vbox:
        xfill True
        spacing phone.px(12)

        null height phone.px(18)
        text (dialed or " ") style "phone_calls_dialed" substitute False
        text (match.name if match is not None else " ") style "phone_calls_dialed_name" substitute False
        null height phone.px(4)

        grid 3 4:
            xalign 0.5
            xspacing phone.px(26)
            yspacing phone.px(14)
            for key, letters in phone.KEYPAD:
                button:
                    style "phone_calls_key"
                    action phone.KeypadPress(key)
                    alt key
                    vbox:
                        align (0.5, 0.5)
                        text key style "phone_calls_key_digit"
                        if letters:
                            text letters style "phone_calls_key_letters"

        null height phone.px(6)

        hbox:
            xalign 0.5
            spacing phone.px(26)
            null width phone.px(82)
            use phone_calls_round_button("✆", "success", None, phone.DialNumber(), size=82)
            if dialed:
                textbutton "⌫":
                    style "phone_calls_backspace"
                    action phone.KeypadDelete()
                    alt _("Delete")
            else:
                null width phone.px(82)


## Full-phone incoming call. phone.incoming_call() shows the phone here and
## waits for Return("accept") or Return("decline").
screen phone_calls_incoming(who, can_decline=True):
    add phone.color("call_bg")

    use phone_calls_caller(who, _("incoming call"), pulse=True)

    hbox:
        xalign 0.5
        yalign 0.86
        spacing phone.px(120)
        if can_decline:
            use phone_calls_round_button("✕", "danger", _("Decline"), Return("decline"))
        fixed:
            fit_first True
            at phone_calls_bob
            use phone_calls_round_button("✆", "success", _("Accept"), Return("accept"))


## An outgoing call that nobody picks up. It closes by itself.
screen phone_calls_outgoing(who, uid=None):
    $ elapsed = phone.outgoing_elapsed(uid)

    timer 0.2 repeat True action phone._OutgoingTick(uid)

    add phone.color("call_bg")

    use phone_calls_caller(who, (_("calling…") if elapsed < phone.OUTGOING_NO_ANSWER else _("No answer")), pulse=(elapsed < phone.OUTGOING_NO_ANSWER))

    hbox:
        xalign 0.5
        yalign 0.86
        use phone_calls_round_button("✕", "danger", _("End"), phone.Back())


## Avatar, name and a status line, centered at the top of a call screen.
screen phone_calls_caller(who, status=None, pulse=False):
    vbox:
        xalign 0.5
        ypos phone.px(70)
        spacing phone.px(8)

        fixed:
            xysize (phone.px(220), phone.px(220))
            xalign 0.5
            if pulse:
                add phone.circle("call_text", phone.px(150)) at phone_calls_pulse(0.0) align (0.5, 0.5)
                add phone.circle("call_text", phone.px(150)) at phone_calls_pulse(0.8) align (0.5, 0.5)
            add phone.caller_avatar(who, phone.px(150)) align (0.5, 0.5)

        text phone.caller_name(who) style "phone_calls_caller_name" substitute False
        if status:
            text status style "phone_calls_status"
        if phone.is_contact_key(who) and phone.caller_number(who):
            text phone.caller_number(who) style "phone_calls_status" substitute False


## A round call button with a caption.
screen phone_calls_round_button(glyph, key, caption, action, size=76, label_style="phone_calls_round_label"):
    vbox:
        spacing phone.px(8)
        button:
            style "phone_calls_round"
            xysize (phone.px(size), phone.px(size))
            xalign 0.5
            background phone.circle(key, phone.px(size))
            hover_background Transform(phone.circle(key, phone.px(size)), alpha=0.8)
            insensitive_background Transform(phone.circle(key, phone.px(size)), alpha=0.4)
            action action
            alt (caption or glyph)
            text glyph style "phone_calls_round_glyph" size phone.px(size * 0.42)
        if caption:
            text caption style label_style


## In-call overlay: sits at the top of the screen during the conversation.
## It is not modal, so the dialogue below it works as usual.
screen phone_calls_active():
    style_prefix "phone"

    $ call = phone.active_call()

    if call is not None and not phone.is_open():
        frame:
            style "phone_calls_pill"

            hbox:
                spacing phone.px(12)
                add phone.caller_avatar(call.who, phone.px(44)) yalign 0.5
                vbox:
                    yalign 0.5
                    xminimum phone.px(120)
                    text phone.caller_name(call.who) style "phone_calls_pill_name" substitute False
                    add DynamicDisplayable(phone._call_timer_text)
                if call.label:
                    null width phone.px(8)
                else:
                    button:
                        style "phone_calls_round"
                        xysize (phone.px(44), phone.px(44))
                        yalign 0.5
                        background phone.circle("danger", phone.px(44))
                        hover_background Transform(phone.circle("danger", phone.px(44)), alpha=0.8)
                        action phone.HangUp()
                        alt _("Hang up")
                        text "✕" style "phone_calls_round_glyph" size phone.px(20)
