# Wallpapers app: a two-column grid of previews and a full-display preview.

screen phone_wallpapers():
    $ items = phone.all_wallpapers()
    $ tw, th = phone.wallpaper_tile_size()

    use phone_page(_("Wallpapers")):
        if not items:
            use phone_empty(_("No wallpapers yet"))
        else:
            viewport:
                scrollbars "vertical"
                mousewheel True
                draggable True
                pagekeys True
                yfill True

                vbox:
                    style "phone_wallpapers_grid"

                    null height phone.px(2)

                    for i in range(0, len(items), 2):
                        hbox:
                            style "phone_wallpapers_grid_row"
                            for entry in items[i:i + 2]:
                                use phone_wallpapers_tile(entry, tw, th)

                    null height phone.px(2)


screen phone_wallpapers_tile(entry, tw, th):
    $ wid, image, name, locked = entry
    $ unlocked = phone.wallpaper_unlocked(wid)
    $ current = phone.current_wallpaper() == wid
    $ ring = phone.px(4)

    button:
        style "phone_wallpapers_tile"
        action phone.PreviewWallpaper(wid)
        alt name

        vbox:
            spacing phone.px(8)

            fixed:
                xysize (tw + 2 * ring, th + 2 * ring)

                if current:
                    add Transform(phone.rounded("accent", "md"), xysize=(tw + 2 * ring, th + 2 * ring))
                else:
                    add Transform(phone.rounded("divider", "md"), xysize=(tw + 2 * ring, th + 2 * ring)) alpha 0.6

                fixed:
                    pos (ring, ring)
                    xysize (tw, th)
                    add phone.wallpaper_thumbnail(wid, tw, th, dim=not unlocked)

                    if unlocked:
                        text phone.clock_text() style "phone_wallpapers_tile_clock" substitute False
                    else:
                        add phone.lock_icon(phone.px(40)) align (0.5, 0.5)

                    if current:
                        fixed:
                            xysize (phone.px(30), phone.px(30))
                            xalign 1.0
                            yalign 1.0
                            offset (-phone.px(10), -phone.px(10))
                            add phone.circle("accent", phone.px(30))
                            text "✓" style "phone_wallpapers_check"

                    if unlocked and phone.wallpaper_is_new(wid):
                        frame:
                            style "phone_wallpapers_new"
                            text _("New") style "phone_wallpapers_new_text"

            text name style ("phone_wallpapers_tile_name_current" if current else "phone_wallpapers_tile_name")


screen phone_wallpapers_preview(wallpaper):
    $ entry = phone.wallpaper_entry(wallpaper)
    $ cw, ch = phone.content_size()

    if entry is None:
        use phone_page(_("Wallpaper")):
            use phone_empty(_("This wallpaper is no longer available."))
    else:
        $ unlocked = phone.wallpaper_unlocked(wallpaper)
        $ current = phone.current_wallpaper() == wallpaper

        fixed:
            xysize (cw, ch)

            add phone.wallpaper_preview_image(wallpaper)

            if unlocked:
                # Same place as the home screen clock.
                vbox:
                    xfill True
                    null height phone.px(30)
                    text phone.clock_text() style "phone_home_clock" substitute False
            else:
                add Solid("#000000a0")
                vbox:
                    align (0.5, 0.4)
                    spacing phone.px(16)
                    add phone.lock_icon(phone.px(64)) xalign 0.5
                    text _("Locked") style "phone_wallpapers_preview_note" xalign 0.5
                    text _("Keep playing to unlock this wallpaper.") style "phone_wallpapers_preview_hint"

            frame:
                style "phone_wallpapers_preview_panel"

                vbox:
                    xfill True
                    spacing phone.px(14)

                    text entry[2] style "phone_wallpapers_preview_name"

                    hbox:
                        xalign 0.5
                        spacing phone.px(12)

                        textbutton _("Cancel"):
                            style "phone_wallpapers_preview_cancel"
                            action phone.Back()

                        if current:
                            textbutton _("Current"):
                                style "phone_wallpapers_preview_set"
                                action NullAction()
                                sensitive False
                        elif unlocked:
                            textbutton _("Set wallpaper"):
                                style "phone_wallpapers_preview_set"
                                action phone.SetWallpaper(wallpaper)
