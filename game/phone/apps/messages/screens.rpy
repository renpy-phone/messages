# Screens of the Messages app: the inbox and a conversation.

## One dot of the typing indicator; `delay` staggers the three dots.
transform phone_messages_typing_pulse(delay=0.0):
    alpha 0.3
    pause delay
    block:
        ease 0.4 alpha 1.0
        ease 0.4 alpha 0.3
        pause 0.3
        repeat


## Inbox: conversations, newest first.
screen phone_messages():
    $ conversations = phone.messages_state.inbox()

    use phone_page(_("Messages")):
        if conversations:
            use phone_list():
                for conv in conversations:
                    use phone_row(
                        phone.short_title(conv.id),
                        subtitle=phone.inbox_preview(conv),
                        image=phone.thread_avatar(conv.id, phone.px(52)),
                        badge=conv.unread + (1 if conv.choice else 0),
                        note=phone.inbox_time(conv),
                        action=phone.MessagesOpen(conv.id),
                    )
        else:
            use phone_empty(_("No messages yet"))


## One conversation. Pending messages play back with a typing indicator, one
## every phone.cfg.messages_typing_delay seconds, while this screen is shown.
screen phone_messages_thread(thread):
    default yadj = ui.adjustment()

    $ conv = phone.conversation(thread)
    $ is_group = phone.is_group(thread)
    $ entries = conv.log[-phone.cfg.messages_max_rendered:]
    $ playing = bool(conv.pending) and conv.choice is None
    $ typing = playing and conv.next_is_incoming()

    if playing:
        timer max(0.05, phone.cfg.messages_typing_delay) repeat True action phone.MessagesTick(thread, yadj)

    side "t c b":
        xysize phone.content_size()

        # Header: back, avatar and name.
        vbox:
            frame:
                style "phone_messages_header"

                hbox:
                    yalign 0.5
                    spacing phone.px(10)

                    imagebutton:
                        style "phone_messages_back"
                        properties phone.art_states("messages/back", (phone.px(40), phone.px(40)))
                        action phone.Back()
                        alt _("Back")

                    add phone.thread_avatar(thread, phone.px(44)) yalign 0.5

                    vbox:
                        yalign 0.5
                        text phone.short_title(thread, 22) style "phone_messages_title" substitute False
                        if is_group:
                            text phone.group_members_line(thread) style "phone_messages_subtitle" substitute False

            use phone_divider

        # The log.
        viewport:
            yadjustment yadj
            yinitial 1.0
            scrollbars "vertical"
            mousewheel True
            draggable True
            yfill True

            frame:
                style "empty"
                xfill True
                padding (phone.px(6), phone.px(14))

                vbox:
                    style "phone_messages_log"

                    if len(conv.log) > len(entries):
                        text _("Earlier messages are not shown") style "phone_messages_note"

                    for i, entry in enumerate(entries):
                        $ prev = entries[i - 1] if i else None

                        if entry.kind == "note":
                            null height phone.px(6)
                            text entry.text style "phone_messages_note" substitute False
                            null height phone.px(2)

                        elif entry.kind == "me":
                            use phone_messages_bubble(entry, True, phone.bubble_tail(entries, i, typing))

                        else:
                            if is_group and (prev is None or prev.sender != entry.sender or not prev.incoming):
                                text phone.sender_name(entry.sender):
                                    style "phone_messages_sender"
                                    color phone.contact(entry.sender).tint()
                                    xoffset phone.px(16)
                                    substitute False
                            use phone_messages_bubble(entry, False, phone.bubble_tail(entries, i, typing))

                    if typing:
                        frame:
                            style "phone_messages_bubble_in_tail"
                            hbox:
                                style "phone_messages_typing"
                                for k in range(3):
                                    add phone.art("messages/typing_dot", size=(phone.px(10), phone.px(10))):
                                        yalign 0.5
                                        at phone_messages_typing_pulse(k * 0.15)

        # Reply options, or an idle composer bar.
        frame:
            style "phone_messages_panel"

            if conv.choice:
                vbox:
                    spacing phone.px(8)
                    for option in conv.choice:
                        button:
                            style "phone_messages_reply"
                            action phone.MessagesChoose(thread, option.uid, yadj)
                            alt option.text

                            hbox:
                                xalign 0.5
                                spacing phone.px(10)
                                if option.image is not None:
                                    add phone.thumbnail(option.image, phone.px(44), 1.0) yalign 0.5
                                if option.text:
                                    text option.text style "phone_messages_reply_text" yalign 0.5 substitute False
            else:
                frame:
                    style "phone_messages_composer"
                    text (_("Typing…") if typing else _("Message")) style "phone_messages_composer_text"


## A message bubble: incoming on the left, the player's on the right. The
## last bubble of a run from one sender has a tail.
screen phone_messages_bubble(entry, out, tail=False):
    frame:
        style "phone_messages_bubble_{}{}".format("out" if out else "in", "_tail" if tail else "")

        if entry.image is not None:
            # The bubble art has an 8px gutter on the sender's side.
            if entry.text:
                padding ((phone.px(4), phone.px(4), phone.px(12), phone.px(10)) if out else (phone.px(12), phone.px(4), phone.px(4), phone.px(10)))
            else:
                # A picture on its own needs no bubble around it.
                background None
                padding ((0, 0, phone.px(8), 0) if out else (phone.px(8), 0, 0, 0))
            vbox:
                spacing phone.px(6)
                button:
                    style "empty"
                    action phone.Navigate("phone_image_viewer", image=entry.image)
                    alt _("Open picture")
                    add phone.thumbnail(entry.image)
                if entry.text:
                    text entry.text:
                        style ("phone_messages_bubble_out_text" if out else "phone_messages_bubble_in_text")
                        xoffset phone.px(10)
                        substitute False
        else:
            text entry.text:
                style ("phone_messages_bubble_out_text" if out else "phone_messages_bubble_in_text")
                substitute False
