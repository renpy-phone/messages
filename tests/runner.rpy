## Headless test runner. tools/test.sh starts the game with PHONE_TESTS=1;
## every label whose name starts with "test_" is called in turn, failures are
## written to PHONE_TEST_OUT and the game quits.
##
## Tests use `$ expect(condition, "message")` and `$ shot("name")`.

init python:
    import os
    import traceback

    _phone_testing = bool(os.environ.get("PHONE_TESTS"))
    _test_failures = []
    _test_log = []
    _test_current = None

    def expect(condition, message=""):
        if not condition:
            _test_failures.append("{}: {}".format(_test_current, message))

    def expect_eq(actual, expected, message=""):
        if actual != expected:
            _test_failures.append("{}: {} (expected {!r}, got {!r})".format(_test_current, message, expected, actual))

    def shot(name):
        """Renders a frame and saves it to PHONE_SHOTS/<name>-<res>.png."""
        folder = os.environ.get("PHONE_SHOTS")
        if not folder:
            return
        wait(0.6)
        res = "{}x{}".format(config.screen_width, config.screen_height)
        renpy.screenshot(os.path.join(folder, "{}-{}.png".format(name, res)))

    import contextlib

    @contextlib.contextmanager
    def runtime_registry():
        """Lets a test call init-only registry functions (see phone.init_only)."""
        dev = config.developer
        config.developer = False
        try:
            yield
        finally:
            config.developer = dev

    def wait(seconds):
        """Lets the game run for a while, even under the modal phone screen.

        (renpy.pause would never end: its timer sits below the modal phone.)
        """
        renpy.call_screen("_test_wait", seconds=seconds, _zorder=10000)

    def _test_write(extra=None):
        out = os.environ.get("PHONE_TEST_OUT")
        lines = list(_test_log) + ["FAIL " + f for f in _test_failures]
        if extra:
            lines.append(extra)
        lines.append("RESULT {}".format("FAIL" if (_test_failures or extra) else "PASS"))
        text = "\n".join(lines) + "\n"
        if out:
            with open(out, "w") as f:
                f.write(text)
        print(text)

    def _test_exception_handler(short, full, traceback_fn):
        _test_write("ERROR in {}:\n{}".format(_test_current, full))
        os._exit(1)

    if _phone_testing and os.environ.get("PHONE_TEST_WATCHDOG"):
        import faulthandler, sys
        faulthandler.dump_traceback_later(int(os.environ["PHONE_TEST_WATCHDOG"]), exit=True, file=sys.__stderr__)

    if _phone_testing:
        config.exception_handler = _test_exception_handler
        config.window_icon = None

screen _test_wait(seconds):
    timer seconds action Return()

label splashscreen:
    if _phone_testing:
        jump _phone_run_tests
    return

label _phone_run_tests:
    $ _tests = sorted(l for l in renpy.get_all_labels() if l.startswith("test_"))
    $ _test_index = 0
    while _test_index < len(_tests):
        $ _test_current = _tests[_test_index]
        $ _test_log.append("RUN " + _test_current)
        # Every test starts from a fresh phone.
        $ phone.state = phone.PhoneState()
        $ phone.reset_apps()
        call expression _test_current
        $ phone.close()
        $ _test_index += 1
    $ _test_write()
    $ renpy.quit()
