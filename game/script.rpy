## Demo story for the phone framework. Each app has its own short scene in
## game/demo/; this menu lets you try them in any order.

label start:
    scene expression Solid("#1b2330")

    "This demo shows the phone framework. Press P or use the phone button in the corner at any time."

    label .menu:
        menu:
            "Which part of the phone do you want to see?"

            "Messages":
                call demo_messages
            "Photogram":
                call demo_social
            "Phone calls":
                call demo_calls
            "Settings and wallpapers":
                call demo_settings
            "Just open the phone":
                $ phone.open()
            "Finish":
                "Thanks for trying it out."
                return

        jump .menu
