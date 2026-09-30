## Tests for the Settings app.

default _test_settings_hints = False

init python:
    phone.add_toggle_setting("Show hints", "_test_settings_hints", description="Test store toggle", section="Test")
    phone.add_toggle_setting("Skip intro", "_test_settings_skip", persistent=True, section="Test")
    phone.add_action_setting("Credits", ShowMenu("about"), description="Test action row", section="Test")

    def _settings_test_defaults():
        """Persistent preferences outlive a test run, so start from known values."""
        persistent._phone_notifications = None
        persistent._phone_sounds = None
        persistent._phone_clock_24h = None
        persistent._test_settings_skip = None
        phone.set_theme("light")
        phone.set_text_scale(1.0)

    def _settings_test_click(action):
        """Runs a screen action inside an interaction, as a click would."""
        renpy.show_screen("_settings_test_run", action=action, _zorder=10001)
        wait(0.4)

screen _settings_test_run(action):
    timer 0.05 action [Hide("_settings_test_run"), action]

label test_settings_theme:
    $ _settings_test_defaults()
    $ phone.show("settings")
    $ expect_eq(phone.state.current()[0], "phone_settings", "settings opens")
    $ shot("settings-light")

    # The screen's own action: dark mode toggle.
    $ _settings_test_click(phone.SetTheme("dark"))
    $ expect_eq(phone.theme_name(), "dark", "dark mode on")
    $ expect_eq(style.phone_default.color, Color(phone.cfg.themes["dark"]["text"]), "styles are rebuilt")
    $ expect(phone.is_open(), "the phone is still open after the rebuild")
    $ expect_eq(phone.state.current()[0], "phone_settings", "and still on the settings screen")
    $ expect(phone.SetTheme("dark").get_selected(), "SetTheme reports the selection")
    $ shot("settings-dark")

    $ _settings_test_click(phone.SetTheme("light"))
    $ expect_eq(style.phone_default.color, Color(phone.cfg.themes["light"]["text"]), "back to light")
    $ expect(phone.is_open(), "still open")
    $ phone.close()
    return

label test_settings_text_size:
    $ _settings_test_defaults()
    $ phone.show("settings")
    $ expect(phone.SetTextScale(1.0).get_selected(), "Default is selected")
    $ _settings_test_click(phone.SetTextScale(1.2))
    $ expect_eq(phone.text_scale(), 1.2, "Large text")
    $ expect_eq(style.phone_default.size, phone.px(22 * 1.2), "text styles grow")
    $ expect(phone.SetTextScale(1.2).get_selected() and not phone.SetTextScale(1.0).get_selected(), "segment selection follows")
    $ expect(phone.is_open(), "the phone is still open")
    $ shot("settings-large-text")
    $ _settings_test_click(phone.SetTextScale(0.85))
    $ expect_eq(style.phone_default.size, phone.px(22 * 0.85), "text styles shrink")
    $ shot("settings-small-text")
    $ _settings_test_click(phone.SetTextScale(1.0))
    $ expect_eq(style.phone_default.size, phone.px(22), "default size")
    $ phone.close()
    return

label test_settings_clock:
    $ _settings_test_defaults()
    $ expect(phone.clock_24h(), "follows cfg.clock_format (%H:%M) by default")
    $ phone.set_time("21:34")
    $ expect_eq(phone.clock_text(), "21:34", "story time shown as written by default")

    $ phone.SetPreference("clock_24h", False)()
    $ expect(not phone.clock_24h(), "12-hour setting")
    $ expect_eq(phone.clock_text(), "9:34 PM", "story times follow the 12-hour setting")
    $ phone.set_time("00:05")
    $ expect_eq(phone.clock_text(), "12:05 AM", "midnight")
    $ phone.set_time("12:30")
    $ expect_eq(phone.clock_text(), "12:30 PM", "noon")
    $ phone.set_time("Monday")
    $ expect_eq(phone.clock_text(), "Monday", "free text is left alone")

    $ phone.SetPreference("clock_24h", True)()
    $ phone.set_time("9:34 pm")
    $ expect_eq(phone.clock_text(), "21:34", "12-hour story times follow the 24-hour setting")
    $ phone.set_time("7:02")
    $ expect_eq(phone.clock_text(), "07:02", "padded")

    python:
        import re, time
        phone.set_time(None)
        expect(re.match(r"^\d\d:\d\d$", phone.clock_text()), "real time, 24 hours")
        persistent._phone_clock_24h = False
        expect(re.match(r"^\d{1,2}:\d\d [AP]M$", phone.clock_text()), "real time, 12 hours")

    $ phone.set_time("21:34")
    $ phone.show("settings")
    $ shot("settings-12h")
    $ phone.close()
    $ _settings_test_defaults()
    return

label test_settings_notifications:
    $ _settings_test_defaults()
    $ phone.show("settings")
    $ _settings_test_click(phone.SetPreference("notifications", False))
    $ expect(not phone.notifications_enabled(), "banners off")
    $ expect(persistent._phone_notifications is False, "stored in persistent")
    $ phone.close()
    $ phone.notify("Eileen", "Hello")
    $ expect(renpy.get_screen("phone_notification", layer=phone.cfg.layer) is None, "no banner when turned off")

    $ phone.SetPreference("notifications", True)()
    $ phone.notify("Eileen", "Hello")
    $ expect(renpy.get_screen("phone_notification", layer=phone.cfg.layer) is not None, "banner when turned on")
    $ renpy.hide_screen("phone_notification", layer=phone.cfg.layer)

    $ phone.SetPreference("sounds", False)()
    $ expect(not phone.sounds_enabled(), "sounds off")
    $ phone.SetPreference("sounds", True)()
    $ expect(phone.sounds_enabled(), "sounds on")
    $ _settings_test_defaults()
    return

label test_settings_custom:
    $ _settings_test_defaults()
    python:
        from renpy.compat.pickle import dumps, loads
        sections = phone.custom_setting_sections()
        expect_eq([t for t, rows in sections], ["Test"], "custom section")
        rows = sections[0][1]
        expect_eq([r.label for r in rows], ["Show hints", "Skip intro", "Credits"], "rows in order")
        hints, skip, credits = rows

        expect(not hints.value(), "store toggle starts off")
        hints.action()()
        expect(_test_settings_hints is True, "store toggle flips the variable")
        expect(hints.value(), "and reads it back")

        expect(not skip.value(), "persistent toggle starts off")
        skip.action()()
        expect(persistent._test_settings_skip is True, "persistent toggle flips persistent")

        # Rows only hold names and actions, so they can be saved safely.
        for r in rows:
            loads(dumps(r.action()))
        expect_eq(loads(dumps(hints.action())), hints.action(), "store toggle action pickles")
        expect_eq(loads(dumps(skip.action())).field, "_test_settings_skip", "persistent toggle action pickles")

        # Re-adding a row replaces it rather than duplicating it. (Normally
        # init-only; allowed here by leaving developer mode for a moment.)
        with runtime_registry():
            phone.add_toggle_setting("Show hints", "_test_settings_hints", description="Replaced", section="Test")
            expect_eq(len(phone.custom_setting_sections()[0][1]), 3, "no duplicates")
            expect_eq(phone.custom_setting_sections()[0][1][0].description, "Replaced", "replaced")
            phone.add_toggle_setting("Show hints", "_test_settings_hints", description="Test store toggle", section="Test")

    $ phone.show("settings", scroll=1.0)
    $ shot("settings-bottom")
    $ phone.set_theme("dark")
    $ shot("settings-bottom-dark")
    $ phone.close()

    # The wallpaper row launches the Wallpapers app.
    $ phone.show("settings")
    $ phone.Launch("wallpapers")()
    $ expect_eq(phone.state.app, "wallpapers", "wallpaper row target")
    $ phone.close()
    $ _settings_test_defaults()
    $ _test_settings_hints = False
    return
