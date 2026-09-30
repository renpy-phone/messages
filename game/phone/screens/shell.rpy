# The phone itself: device frame, status bar, the open app (or the home
# screen) and the navigation bar. Apps never show their own top-level screen;
# their screen is `use`d here, inside a fixed of phone.content_size().

transform phone_device_in:
    on show:
        yoffset phone.px(60) alpha 0.0
        easein 0.2 yoffset 0 alpha 1.0
    on hide:
        easeout 0.15 yoffset phone.px(60) alpha 0.0

screen phone():
    modal True
    style_prefix "phone"

    $ current_screen, current_kwargs = phone.state.current()
    $ screen_bg = phone.screen_background(current_screen) if current_screen is not None else None
    # Transparent status and nav bars over a wallpaper or a screen background.
    $ transparent_bars = current_screen is None or screen_bg is not None

    if phone.cfg.dim_background:
        add phone.cfg.dim_background

    if phone.cfg.close_on_background_click:
        dismiss action phone.Close()

    key "game_menu" action phone.Dismiss()

    frame:
        style "phone_device"
        at phone_device_in, Transform(zoom=phone.cfg.zoom)
        xalign phone.cfg.xalign
        yalign phone.cfg.yalign

        # Swallows clicks on the device so they don't reach `dismiss`.
        button:
            style "empty"
            xfill True
            yfill True
            keyboard_focus False
            action NullAction()

        fixed:
            style "phone_display"

            if current_screen is None:
                $ wallpaper = phone.wallpaper_image()
                if wallpaper is None:
                    add phone.color("wallpaper")
                else:
                    add phone.cover(wallpaper, *phone.display_size())
            elif screen_bg is not None:
                add screen_bg
            else:
                add phone.color("bg")

            vbox:
                use phone_status_bar(on_wallpaper=transparent_bars)

                fixed:
                    style "phone_content"

                    if current_screen is None:
                        use phone_home
                    else:
                        use expression current_screen pass (**current_kwargs)

                use phone_nav_bar(on_wallpaper=transparent_bars)


screen phone_status_bar(on_wallpaper=False):
    frame:
        style "phone_status_bar"
        if not on_wallpaper:
            background phone.color("surface")

        $ status_color = phone.color("status_text" if on_wallpaper else "text")

        text phone.clock_text() style "phone_status_text" color status_color xalign 0.0 substitute False
        hbox:
            xalign 1.0
            yalign 0.5
            spacing phone.px(6)
            text "▂▄▆" style "phone_status_text" font phone.GLYPH_FONT color status_color size phone.px(14)
            text "[phone.state.battery]%" style "phone_status_text" color status_color

        # Re-render once a second so the real-time clock keeps up.
        if phone.state.clock is None:
            timer 1.0 repeat True action NullAction()


screen phone_nav_bar(on_wallpaper=False):
    frame:
        style "phone_nav_bar"
        if not on_wallpaper:
            background phone.color("surface")

        hbox:
            xalign 0.5
            textbutton "‹":
                style "phone_nav_button"
                action phone.Back()
                sensitive bool(phone.state.nav)
                alt _("Back")
            textbutton "○":
                style "phone_nav_button"
                action phone.Home()
                alt _("Home")
            textbutton "✕":
                style "phone_nav_button"
                action phone.Close()
                alt _("Close phone")


screen phone_home():
    vbox:
        xfill True
        spacing phone.px(24)

        null height phone.px(30)
        text phone.clock_text() style "phone_home_clock" substitute False

        vpgrid:
            cols phone.cfg.home_columns
            xalign 0.5
            spacing phone.px(6)
            mousewheel True

            for app in phone.home_apps():
                use phone_app_button(app)


screen phone_app_button(app):
    button:
        style "phone_app_button"
        action phone.Launch(app.id)
        alt app.name

        vbox:
            xalign 0.5
            spacing phone.px(6)

            # Room for the badge, which pokes out above the icon.
            null height phone.px(10)

            fixed:
                xysize (phone.px(72), phone.px(72))
                xalign 0.5
                add phone.app_icon(app, phone.px(72))

                $ count = app.badge()
                if count:
                    use phone_badge(count, xalign=1.0, yalign=0.0, xoffset=phone.px(8), yoffset=-phone.px(8))

            text app.name style "phone_app_label"
