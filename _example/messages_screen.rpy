screen messages(contact=None):
    tag phone
    modal True

    add "darker_80"

    # Click background to close phone
    button:
        action Hide("phone")

    textbutton _("Exit Phone"):
        action Hide("phone")
        xpos 20
        yalign 1.0
        yoffset -20

    frame:
        background "messages_background"
        align (0.5, 0.5)

        hbox:
            pos (41, 62)
            ysize 93
            spacing 15

            imagebutton:
                idle "phone_back_button"
                action [Hide("message_reply"), Show("messenger_home")]
                yalign 0.5

            add contact.profile_picture:
                yalign 0.5

            text contact.name:
                style "messages_contact_name"
                yalign 0.5

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

        if MessagesService.has_replies(contact):
            fixed:
                xysize (416, 63)
                ypos 780

                imagebutton:
                    idle "phone_reply_button_idle"
                    hover "messenger_reply_button_hover"
                    selected_idle "messenger_reply_button_hover"
                    action [Show("message_reply", contact=contact), SetField(inf_adj, "value", float("inf"))]
                    align (0.5, 0.5)

    if not renpy.get_screen("phone"):
        fixed:
            ysize 69
            ypos 843

            imagebutton:
                idle "phone_home_button_idle"
                hover "phone_home_button_hover"
                action [Hide("message_reply"), Show("phone")]
                align (0.5, 0.5)

    key [ "K_ESCAPE", "K_MENU", "K_PAUSE", "mouseup_3" ]:
        action Hide("phone")
