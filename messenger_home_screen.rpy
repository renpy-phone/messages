screen base_phone(background="phone_screen"):
    modal True

    add "darker_80"

    # Click background to close phone
    button:
        action Phone.get_exit_actions()

    textbutton _("Exit Phone"):
        style "phonebutton"
        action Phone.get_exit_actions()

    frame:
        modal True
        background background
        align (0.5, 0.5)
        xysize (433, 918)

        transclude

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
        action Phone.get_exit_actions()


screen messenger_home():
    tag phone_tag
    modal True

    use base_phone:
        frame:
            background "messenger_home_background"
            xysize (433, 918)

            viewport:
                mousewheel True
                draggable True
                pos (11, 134)
                xysize (416, 709)

                vbox:
                    spacing 5

                    null height 10

                    for contact in messenger.contacts:
                        button:
                            action [Function(renpy.retain_after_load), Show("messenger", contact=contact)]
                            ysize 80

                            add Transform(contact.profile_picture, xysize=(65, 65)) xpos 20 yalign 0.5
                            
                            text contact.name style "nametext" xpos 100 yalign 0.5

                            if MessengerService.has_replies(contact):
                                add "phone_contact_notification" align (1.0, 0.5) xoffset -25

    if config_debug:
        for contact in messenger.contacts:
            if MessengerService.has_replies(contact):
                timer 0.1 action [Function(renpy.retain_after_load), Show("messenger", contact=contact)]
