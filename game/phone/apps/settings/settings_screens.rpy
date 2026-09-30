# Settings app.

## `scroll` is the initial scroll position (0.0 top, 1.0 bottom), e.g.
## phone.open("settings", scroll=1.0) to show the game's own settings.
screen phone_settings(scroll=0.0):
    $ dark = phone.theme_name() == "dark"
    $ wallpapers_app = phone.get_app("wallpapers")

    use phone_page(_("Settings")):
        viewport:
            scrollbars "vertical"
            mousewheel True
            draggable True
            pagekeys True
            yfill True
            yinitial scroll

            vbox:
                xfill True

                use phone_settings_section(_("Display"))
                use phone_toggle(_("Dark mode"), dark, phone.SetTheme("light" if dark else "dark"))

                frame:
                    style "phone_settings_item"
                    vbox:
                        xfill True
                        spacing phone.px(10)
                        text _("Text size") style "phone_row_title"
                        use phone_segmented([(label, phone.SetTextScale(scale)) for label, scale in phone.text_sizes])
                use phone_divider

                if wallpapers_app is not None and wallpapers_app.is_installed() and phone.all_wallpapers():
                    $ wid = phone.current_wallpaper()
                    use phone_settings_link(
                        _("Wallpaper"),
                        (phone.wallpaper_name(wid) if wid else _("Theme color")),
                        phone.Launch("wallpapers"),
                        image=phone.wallpaper_thumbnail(wid, phone.px(28), phone.px(56), ("settings/thumbnail_mask", 8)),
                        )

                use phone_settings_section(_("Notifications"))
                use phone_toggle(
                    _("Banners"),
                    phone.notifications_enabled(),
                    phone.SetPreference("notifications", not phone.notifications_enabled()),
                    description=_("Alerts while the phone is away"),
                    )
                use phone_toggle(
                    _("Sounds"),
                    phone.sounds_enabled(),
                    phone.SetPreference("sounds", not phone.sounds_enabled()),
                    )

                use phone_settings_section(_("Clock"))
                use phone_toggle(
                    _("24-hour time"),
                    phone.clock_24h(),
                    phone.SetPreference("clock_24h", not phone.clock_24h()),
                    description=phone.clock_text(),
                    )

                for section, rows in phone.custom_setting_sections():
                    use phone_settings_section(section)
                    for setting in rows:
                        if isinstance(setting, phone.ToggleSetting):
                            use phone_toggle(setting.label, setting.value(), setting.action(), description=setting.description)
                        else:
                            use phone_settings_action(setting.label, setting.description, setting.action())

                use phone_settings_section(_("About"))
                use phone_settings_info(_("Name"), phone.cfg.device_name)
                use phone_settings_info(_("Owner"), phone.player_name())
                use phone_settings_info(_("Model"), phone.cfg.device_model)
                use phone_settings_info(_("Software"), phone.cfg.software_version)

                null height phone.px(24)


## Section title above a group of rows.
screen phone_settings_section(title):
    frame:
        style "phone_settings_section"
        text title style "phone_settings_section_text"
    use phone_divider


## A row that opens something: label on the left, value, image and ›.
screen phone_settings_link(label, value, action, image=None):
    button:
        style "phone_row"
        action action

        fixed:
            ysize max(phone.px(56), phone.text_px(40))
            text label style "phone_row_title" yalign 0.5
            hbox:
                xalign 1.0
                yalign 0.5
                spacing phone.px(12)
                text value style "phone_settings_info_value" substitute False
                if image is not None:
                    add image yalign 0.5
                add phone.art("common/chevron", size=phone.settings_chevron_size()) yalign 0.5
    use phone_divider


## A row added with phone.add_action_setting(): label, optional description
## and a chevron on the right.
screen phone_settings_action(label, description, action):
    button:
        style "phone_row"
        properties phone.art_layer_states("common/chevron", phone.settings_chevron_size(), "foreground", xalign=1.0, yalign=0.5, xoffset=-phone.px(12))
        action action

        vbox:
            yalign 0.5
            xsize phone.px(330)
            text label style "phone_row_title" substitute False
            if description:
                text description style "phone_row_subtext" substitute False
    use phone_divider


## A label and a value, not tappable.
screen phone_settings_info(label, value):
    frame:
        style "phone_settings_item"
        hbox:
            xfill True
            text label style "phone_settings_info_label"
            text value style "phone_settings_info_value"
    use phone_divider


## Segmented control: a row of mutually exclusive choices.
## options is a list of (label, action); the selected one is the one whose
## action reports itself as selected.
screen phone_segmented(options):
    $ inner = phone.content_size()[0] - 2 * phone.px(16) - 2 * phone.px(3)
    frame:
        style "phone_segmented"
        hbox:
            for label, action in options:
                textbutton label:
                    style "phone_segmented_button"
                    xsize (inner // max(1, len(options)))
                    action action
