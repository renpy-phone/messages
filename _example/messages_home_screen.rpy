screen messages_home():
    tag phone
    modal True

    add "darker_80"

    # Click background to close phone
    button:
        action Hide("phone")

    textbutton _("Exit Phone"):
        action Hide("phone")
        xpos 2100
        yalign 1.0
        yoffset -100

    frame:
        background "messages_home_background"
        align (0.5, 0.5)
        xysize renpy.load_surface(renpy.displayable("messages_home_background")).get_size()

        vpgrid:
            cols 1
            mousewheel True
            draggable True
            spacing 5
            align (0.5, 0.5)

            for contact in messages.contacts:
                button:
                    action [Function(renpy.retain_after_load), Show("messages", contact=contact)]

                    add contact.profile_picture yalign 0.5
                    
                    text contact.name:
                        style "messages_contact_name"
                        xpos 100
                        yalign 0.5

                    if MessagesService.has_replies(contact):
                        add "phone_contact_notification" align (1.0, 0.5) xoffset -25

    # if not renpy.get_screen("phone"):
    #     fixed:
    #         ysize 69
    #         ypos 843

    #         imagebutton:
    #             idle "phone_home_button_idle"
    #             hover "phone_home_button_hover"
    #             action [Hide("message_reply"), Show("phone")]
    #             align (0.5, 0.5)

    key [ "K_ESCAPE", "K_MENU", "K_PAUSE", "mouseup_3" ]:
        action Hide("phone")
