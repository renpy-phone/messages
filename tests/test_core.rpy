## Tests for the phone shell, navigation, contacts and apps registry.

init python:
    class _TestApp(phone.App):
        id = "test_app"
        name = "Test"
        screen = "phone_test_app"
        icon = Solid("#8e8e93")
        order = 999
        installed = False

        def badge(self):
            return 3 if phone.state.battery < 50 else 0

    phone.register_app(_TestApp())

define _test_contact = phone.Contact("test_contact", "Tess [_test_surname]", number="555-0100")
default _test_surname = "Ter"

screen phone_test_app(page=1):
    use phone_page(_("Test app")):
        text "Page [page]"

label test_core_contacts:
    $ c = phone.contact("test_contact")
    $ expect(c is _test_contact, "contact lookup returns the defined object")
    $ expect_eq(c.name, "Tess Ter", "names are interpolated")
    $ expect(not c.known, "contacts start unknown")
    $ phone.add_contact(c)
    $ expect(c.known, "add_contact makes a contact known")
    $ phone.rename_contact("test_contact", "Tessa")
    $ expect_eq(c.name, "Tessa", "rename_contact")
    $ missing = phone.contact("nobody")
    $ expect_eq(missing.name, "nobody", "unknown ids resolve to a placeholder")
    python:
        from renpy.compat.pickle import dumps, loads
        expect(loads(dumps(c)) is c, "pickled contacts resolve to the registry object")
    return

label test_core_navigation:
    $ expect(not phone.is_open(), "phone starts closed")
    $ expect(_TestApp() .id not in [a.id for a in phone.home_apps()], "uninstalled apps are hidden")
    $ phone.install_app("test_app")
    $ expect("test_app" in [a.id for a in phone.home_apps()], "install_app shows the app")
    $ phone.show()
    $ expect(phone.is_open(), "phone.show opens the phone")
    $ expect_eq(phone.state.current(), (None, {}), "opens on the home screen")
    $ shot("core-home")
    $ phone.Launch("test_app")()
    $ expect_eq(phone.state.current()[0], "phone_test_app", "Launch shows the app screen")
    $ phone.Navigate("phone_test_app", page=2)()
    $ expect_eq(phone.state.current(), ("phone_test_app", {"page": 2}), "Navigate pushes a screen")
    $ shot("core-app")
    $ phone.Back()()
    $ expect_eq(phone.state.current()[1], {}, "Back pops")
    $ phone.Dismiss()()
    $ expect_eq(phone.state.current(), (None, {}), "Dismiss goes home")
    $ phone.Dismiss()()
    $ wait(0.3)
    $ expect(not phone.is_open(), "Dismiss on the home screen closes")
    $ phone.set_battery(20)
    $ expect_eq(phone.total_badges(), 3, "badges add up")
    $ phone.uninstall_app("test_app")
    return

label test_core_open_blocks:
    # phone.open() waits in call_screen; close it from a timer.
    show screen _test_closer
    $ phone.open("test_app")
    $ expect(not phone.is_open(), "Close returns from phone.open")
    return

screen _test_closer():
    timer 0.5 action [Hide("_test_closer"), phone.Close()]

label test_core_state_pickles:
    python:
        from renpy.compat.pickle import dumps, loads
        phone.state.navigate("phone_test_app", page=3)
        s = loads(dumps(phone.state))
        expect_eq(s.nav, phone.state.nav, "state survives pickling")
    return

label test_core_theme_rebuild:
    $ phone.set_theme("dark")
    $ expect_eq(style.phone_default.color, Color(phone.cfg.themes["dark"]["text"]), "set_theme rebuilds styles")
    $ phone.set_text_scale(1.5)
    $ expect_eq(style.phone_default.size, phone.text_px(22), "set_text_scale rebuilds styles")
    $ phone.show()
    $ shot("core-dark-home")
    $ phone.close()
    $ phone.set_text_scale(1.0)
    $ phone.set_theme("light")
    $ expect_eq(style.phone_default.color, Color(phone.cfg.themes["light"]["text"]), "theme switches back")
    return

label test_core_close_ends_open:
    # phone.close() from a screen must end phone.open(), not leave it stuck.
    show screen _test_function_closer
    $ phone.open()
    $ expect(not phone.is_open(), "Function(phone.close) returns from phone.open")
    return

screen _test_function_closer():
    timer 0.5 action [Hide("_test_function_closer"), Function(phone.close)]

label test_core_after_load_registered:
    $ expect(phone._core_after_load in config.after_load_callbacks, "core migration hook is registered")
    python:
        s = phone.state
        del s.__dict__["battery"]
        phone._core_after_load()
        expect_eq(s.battery, 100, "missing fields are restored on load")
    return

label test_core_player_name:
    default _test_pov = "Alex"
    $ expect_eq(phone.player_name(), phone.cfg.player_name, "defaults to cfg")
    $ phone.set_player_name("[_test_pov]", handle="alex_99")
    $ expect_eq(phone.player_name(), "Alex", "runtime name is interpolated")
    $ expect_eq(phone.player_handle(), "alex_99", "runtime handle")
    return

label test_core_subclass_app:
    python:
        class _TestAppV2(_TestApp):
            name = "Test v2"
        with runtime_registry():
            phone.register_app(_TestAppV2())
        expect_eq(phone.get_app("test_app").name, "Test v2", "a subclass can replace an app")
        try:
            class _Other(phone.App):
                id = "test_app"
                screen = "phone_test_app"
            with runtime_registry():
                phone.register_app(_Other())
            expect(False, "an unrelated app cannot take an id")
        except Exception:
            pass
        phone.apps["test_app"] = _TestApp()
    return

label test_core_clock_ticks:
    $ phone.set_time("09:41")
    $ phone.show()
    $ shot("core-story-clock")
    $ phone.set_time("09:42")
    $ wait(1.2)
    $ phone.close()
    $ phone.set_time(None)
    return

label test_core_memo_cache:
    python:
        a = phone.cover("images/demo/beach.png", 40, 40)
        b = phone.cover("images/demo/beach.png", 40, 40)
        expect(a is b, "cover() is cached")
        c = phone.avatar("test_contact", 40)
        phone.rename_contact("test_contact", "Zed")
        d = phone.avatar("test_contact", 40)
        expect(c is not d, "avatar cache follows contact changes")
        phone.set_theme("dark")
        expect(phone.cover("images/demo/beach.png", 40, 40) is not a, "cache is per theme")
        phone.set_theme("light")
    return
