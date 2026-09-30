## Settings and Wallpapers demo.

# A wallpaper the player earns during the scene. Locked wallpapers stay dimmed
# in the Wallpapers app until phone.unlock_wallpaper() is called.
init python:
    phone.add_wallpaper("demo_beach", "demo photo beach", _("Beach Day"), locked=True)

label demo_settings:
    e "New phone? Let me guess, the first thing you do is dig through the settings."
    e "Dark mode, bigger text, a 24-hour clock... it's all in there."

    $ phone.open("settings")

    e "Oh, and I took this picture at the beach. You can have it."

    # Shows a "New wallpaper unlocked" banner and badges the Wallpapers app.
    $ phone.unlock_wallpaper("demo_beach")

    e "Go set it as your wallpaper. Open the Wallpapers app, or tap Wallpaper in Settings."

    $ phone.open()

    if phone.current_wallpaper() == "demo_beach":
        e "Looks great on you!"
    else:
        e "No? Well, it's there whenever you want it."

    return
