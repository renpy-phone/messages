## Tests for the Wallpapers app.

init python:
    phone.add_wallpaper("test_locked", Solid("#c0392b"), "Test Locked", locked=True)

screen _wallpapers_test_run(action):
    timer 0.05 action [Hide("_wallpapers_test_run"), action]

init python:
    def _wallpapers_test_click(action):
        """Runs a screen action inside an interaction, as a click would."""
        renpy.show_screen("_wallpapers_test_run", action=action, _zorder=10001)
        wait(0.4)

label test_wallpapers_registry:
    $ ids = [w[0] for w in phone.all_wallpapers()]
    $ expect(len([i for i in ids if i in ("aurora", "dusk", "night", "lagoon", "coral", "graphite")]) == 6, "six built-in wallpapers")
    $ expect(phone.wallpaper_entry(phone.cfg.default_wallpaper) is not None, "the default wallpaper exists")
    $ expect_eq(phone.current_wallpaper(), phone.cfg.default_wallpaper, "starts on the default")
    $ expect(phone.wallpaper_image() is phone.wallpaper_entry(phone.cfg.default_wallpaper)[1], "home uses the default")
    $ expect_eq(phone.wallpaper_name("night"), "Night Sky", "names")
    $ expect(phone.wallpaper_unlocked("dusk"), "built-ins are unlocked")
    $ expect(not phone.wallpaper_unlocked("nope"), "unknown ids are not unlocked")

    python:
        # The built-ins are picture files, and the app's art is all there.
        for wid in ("aurora", "dusk", "night", "lagoon", "coral", "graphite"):
            image = phone.wallpaper_entry(wid)[1]
            expect(isinstance(image, str) and image.startswith("gui/phone/wallpapers/") and renpy.loadable(image),
                   "built-in wallpaper {} is a picture file".format(wid))
        for theme in ("light", "dark"):
            phone.set_theme(theme)
            for state in ("idle", "hover", "selected_idle", "selected_hover"):
                expect((phone.art_path("wallpapers/tile", state) or "").endswith("wallpapers/tile_{}.png".format(state)),
                       "tile outline {} ({})".format(state, theme))
            expect((phone.art_path("wallpapers/set_button", "insensitive") or "").endswith("set_button_insensitive.png"), "Current button art")
        phone.set_theme("light")
        expect(phone.has_art("wallpapers/lock") and phone.has_art("wallpapers/mask"), "lock and mask art")

    $ phone.set_wallpaper("dusk")
    $ expect_eq(phone.state.wallpaper, "dusk", "set_wallpaper saves the id in phone.state")
    $ expect_eq(phone.current_wallpaper(), "dusk", "current_wallpaper")
    $ expect(phone.wallpaper_image() is phone.wallpaper_entry("dusk")[1], "set_wallpaper is reflected by wallpaper_image()")
    $ phone.set_wallpaper(None)
    $ expect_eq(phone.current_wallpaper(), phone.cfg.default_wallpaper, "None returns to the default")

    # A save whose wallpaper no longer exists falls back to the default.
    $ phone.state.wallpaper = "removed_in_an_update"
    $ expect(phone.wallpaper_image() is phone.wallpaper_entry(phone.cfg.default_wallpaper)[1], "unknown saved wallpaper falls back")
    $ expect_eq(phone.current_wallpaper(), phone.cfg.default_wallpaper, "current_wallpaper falls back too")

    python:
        try:
            phone.set_wallpaper("nope")
            expect(False, "set_wallpaper rejects unknown ids")
        except Exception:
            pass

        # Plain 3-tuples appended by a game are accepted.
        phone.cfg.wallpapers.append(("test_plain", Solid("#123"), None))
        expect_eq(phone.wallpaper_entry("test_plain")[2:], ("Test Plain", False), "3-tuple entries")
        with runtime_registry():
            phone.remove_wallpaper("test_plain")
        expect(phone.wallpaper_entry("test_plain") is None, "remove_wallpaper")
    return

label test_wallpapers_unlock:
    $ expect(not phone.wallpaper_unlocked("test_locked"), "locked wallpapers start locked")
    $ expect(not phone.SetWallpaper("test_locked").get_sensitive(), "locked ones cannot be picked")
    $ expect_eq(phone.get_app("wallpapers").badge(), 0, "no badge")

    $ expect(phone.unlock_wallpaper("test_locked"), "unlock returns True the first time")
    $ expect(phone.wallpaper_unlocked("test_locked"), "unlocked")
    $ expect(renpy.get_screen("phone_notification", layer=phone.cfg.layer) is not None, "unlocking shows a banner")
    $ shot("wallpapers-unlock-banner")
    $ renpy.hide_screen("phone_notification", layer=phone.cfg.layer)
    $ expect_eq(phone.get_app("wallpapers").badge(), 1, "new wallpapers badge the app")
    $ expect(not phone.unlock_wallpaper("test_locked"), "unlocking twice returns False")

    # Looking at it in the app clears the badge.
    $ phone.show("wallpapers")
    $ phone.PreviewWallpaper("test_locked")()
    $ expect_eq(phone.state.current(), ("phone_wallpapers_preview", {"wallpaper": "test_locked"}), "preview opens")
    $ expect_eq(phone.get_app("wallpapers").badge(), 0, "preview clears the badge")
    $ phone.SetWallpaper("test_locked")()
    $ expect_eq(phone.current_wallpaper(), "test_locked", "picked")
    $ phone.close()

    $ phone.lock_wallpaper("test_locked")
    $ expect(not phone.wallpaper_unlocked("test_locked"), "lock_wallpaper locks again")
    $ expect_eq(phone.current_wallpaper(), phone.cfg.default_wallpaper, "locking the current one restores the default")

    # No banner when asked not to.
    $ phone.unlock_wallpaper("test_locked", notify=False)
    $ expect(renpy.get_screen("phone_notification", layer=phone.cfg.layer) is None, "notify=False shows no banner")
    $ phone.lock_wallpaper("test_locked")

    # The script may force a locked wallpaper; that unlocks it quietly.
    $ phone.set_wallpaper("test_locked")
    $ expect(phone.wallpaper_unlocked("test_locked"), "set_wallpaper unlocks")
    $ expect_eq(phone.get_app("wallpapers").badge(), 0, "without a badge")
    return

label test_wallpapers_pickle:
    python:
        from renpy.compat.pickle import dumps, loads
        phone.unlock_wallpaper("test_locked", notify=False)
        phone.set_wallpaper("night")
        s = loads(dumps(phone.wallpapers_state))
        expect_eq(list(s.unlocked), ["test_locked"], "unlocked ids survive pickling")
        expect_eq(list(s.new), ["test_locked"], "new ids survive pickling")
        st = loads(dumps(phone.state))
        expect_eq(st.wallpaper, "night", "the current wallpaper is saved in phone.state")
        a = loads(dumps(phone.SetWallpaper("night")))
        expect_eq(a, phone.SetWallpaper("night"), "actions pickle")
    return

label test_wallpapers_screens:
    # Show the test wallpaper first so the screenshots include it.
    python:
        saved = list(phone.cfg.wallpapers)
        phone.cfg.wallpapers.sort(key=lambda w: w[0] != "test_locked")
    $ phone.show("wallpapers")
    $ shot("wallpapers-grid")
    $ phone.set_theme("dark")
    $ shot("wallpapers-grid-dark")
    $ phone.set_theme("light")

    $ phone.unlock_wallpaper("test_locked", notify=False)
    $ shot("wallpapers-grid-new")

    $ phone.lock_wallpaper("test_locked")
    $ phone.PreviewWallpaper("test_locked")()
    $ shot("wallpapers-preview-locked")
    $ phone.Back()()

    # Tap a tile, then "Set wallpaper", as the player would.
    $ _wallpapers_test_click(phone.PreviewWallpaper("coral"))
    $ expect_eq(phone.state.current()[0], "phone_wallpapers_preview", "tapping a tile opens the preview")
    $ shot("wallpapers-preview")
    $ _wallpapers_test_click(phone.SetWallpaper("coral"))
    $ expect_eq(phone.current_wallpaper(), "coral", "Set wallpaper makes it current")
    $ expect_eq(phone.state.current()[0], "phone_wallpapers", "and returns to the grid")
    $ expect(phone.is_open(), "the phone stays open")
    $ shot("wallpapers-grid-selected")
    $ phone.PreviewWallpaper("coral")()
    $ shot("wallpapers-preview-current")

    $ phone.Home()()
    $ shot("wallpapers-home-coral")
    $ phone.set_wallpaper("night")
    $ shot("wallpapers-home-night")
    $ phone.close()
    $ phone.cfg.wallpapers[:] = saved
    return

label test_wallpapers_empty:
    python:
        saved = list(phone.cfg.wallpapers)
        saved_default = phone.cfg.default_wallpaper
        with runtime_registry():
            phone.clear_wallpapers()
        expect_eq(phone.current_wallpaper(), None, "no wallpapers")
        expect(phone.wallpaper_image() is None, "theme color")
    $ phone.show("wallpapers")
    $ shot("wallpapers-empty")
    $ phone.close()
    python:
        phone.cfg.wallpapers[:] = saved
        phone.cfg.default_wallpaper = saved_default
    return
