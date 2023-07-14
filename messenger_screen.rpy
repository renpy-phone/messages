screen messenger(contact=None):
    tag phone_tag
    modal True

    use base_phone:
        frame:
            background "messenger_conversation_background"
            xysize (433, 918)

            hbox:
                pos (41, 62)
                ysize 93
                spacing 15

                imagebutton:
                    idle "phone_back_button"
                    action [Hide("message_reply"), Show("messenger_home")]
                    yalign 0.5

                add Transform(contact.profile_picture, xysize=(65, 65)) yalign 0.5

                text contact.name style "nametext" yalign 0.5

            viewport:
                yadjustment inf_adj
                mousewheel True
                draggable True
                pos (11, 157)
                xysize (416, 686)

                vbox:
                    xfill True
                    
                    null height 25

                    for message in contact.text_messages:
                        if message.content.strip():
                            frame:
                                if isinstance(message, Reply):
                                    background "phone_reply_background"
                                    xalign 1.0

                                    if renpy.loadable(message.content):
                                        padding (25, 25)

                                        imagebutton:
                                            idle Transform(message.content, zoom=0.15)
                                            action Show("phone_image", img=message.content)
                                    else:
                                        padding (40, 30)

                                        text message.content  style "reply_text"
                                
                                else:
                                    background "phone_message_background"

                                    if renpy.loadable(message.content):
                                        padding (25, 25)

                                        imagebutton:
                                            idle Transform(message.content, zoom=0.15)
                                            action Show("phone_image", img=message.content)
                                    else:
                                        padding (40, 30)

                                        text message.content  style "message_text"

                    null height 75

            if MessengerService.has_replies(contact):
                fixed:
                    xysize (416, 63)
                    ypos 780

                    imagebutton:
                        idle "phone_reply_button_idle"
                        hover "messenger_reply_button_hover"
                        selected_idle "messenger_reply_button_hover"
                        action [Show("message_reply", contact=contact), SetField(inf_adj, "value", float("inf"))]
                        align (0.5, 0.5)

    if config_debug:
        if MessengerService.has_replies(contact):
            timer 0.1 repeat True action Show("message_reply", contact=contact)
        else:
            timer 0.1 repeat True action [Hide("message_reply"), Show("phone")]