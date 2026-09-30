## Minimal screens for the demo project. Real games already have these in
## their screens.rpy; the phone framework does not need them.

style demo_text:
    font "DejaVuSans.ttf"
    size 30
    color "#ffffff"

# The say screen's id'd displayables always get these three style names.
style window:
    xfill True
    yalign 1.0
    ysize 220
    background Solid("#000000b0")
    padding (320, 30, 320, 30)

style demo_name is demo_text:
    size 32
    bold True

style say_label is demo_name
style say_dialogue is demo_text

style demo_choice_button:
    xsize 800
    xalign 0.5
    padding (20, 14)
    background Solid("#000000b0")
    hover_background Solid("#1e88e5d0")

style demo_choice_button_text is demo_text:
    xalign 0.5
    text_align 0.5

screen say(who, what):
    window:
        id "window"
        vbox:
            spacing 10
            if who is not None:
                text who id "who"
            text what id "what"

    # P opens or closes the phone from anywhere in the story.
    key "K_p" action phone.Toggle()

screen choice(items):
    style_prefix "demo_choice"

    vbox:
        xalign 0.5
        yalign 0.45
        spacing 16
        for i in items:
            textbutton i.caption action i.action

screen main_menu():
    tag menu
    add Solid("#1b2330")
    vbox:
        align (0.5, 0.45)
        spacing 30
        text "Phone Framework Demo" style "demo_name" size 64 xalign 0.5
        textbutton "Start" action Start() text_style "demo_text" xalign 0.5
        textbutton "Quit" action Quit(confirm=False) text_style "demo_text" xalign 0.5

define config.main_menu_music = None
