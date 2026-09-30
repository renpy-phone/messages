## Tests for the Phone (calls) app.

init python:
    import os

    _calls_timer_count = 0

    def _calls_snap(name):
        """Screenshot without waiting (usable from a timer action)."""
        folder = os.environ.get("PHONE_SHOTS")
        if folder:
            res = "{}x{}".format(config.screen_width, config.screen_height)
            renpy.screenshot(os.path.join(folder, "{}-{}.png".format(name, res)))

    def _calls_note(key, value):
        _calls_seen[key] = value

    def _calls_count(key):
        _calls_seen[key] = _calls_seen.get(key, 0) + 1

    def _calls_note_state(key):
        _calls_seen[key] = {
            "current": phone.state.current(),
            "ringing": phone.calls_state.ringing,
            "open": phone.is_open(),
            "incoming_shown": phone.is_showing("phone_calls_incoming"),
        }

    def _calls_later(delay, *actions):
        """Runs actions from a timer, e.g. to press a button while the script waits."""
        global _calls_timer_count
        _calls_timer_count += 1
        tag = "_calls_timer_{}".format(_calls_timer_count)
        renpy.show_screen("_calls_test_timer", delay, tag, list(actions), _tag=tag, _zorder=10001)

    def _calls_say_callback(event, interact=True, **kwargs):
        if event == "begin":
            _calls_count("say_runs")

    def _calls_call_step():
        """Dials Lucy from her contact card, then closes the phone after the call."""
        s = _calls_seen
        if phone.is_showing("phone_calls_contact") and not s.get("dialed"):
            s["dialed"] = True
            phone.CallContact("lucy")()  # ends the current statement
        elif s.get("lucy_label_done") and phone.is_open() and not s.get("closed"):
            s["closed"] = True
            _calls_note_state("after")
            _calls_snap("calls-after-call")
            return phone.Close()()

screen _calls_test_timer(delay, tag, actions):
    timer delay action [Hide(tag)] + actions

screen _calls_call_driver():
    zorder 10001
    timer 0.4 repeat True action Function(_calls_call_step)

define _calls_narrator = Character(None, callback=_calls_say_callback)

# Notes the tests take along the way (saved, so a test can save and load).
default _calls_seen = {}


# Call labels used by the tests (not tests themselves: no "test_" prefix).

label _test_calls_eileen_call:
    $ _calls_note("in_label_in_call", phone.in_call())
    $ _calls_note("in_label_label_flag", phone.active_call().label)
    $ _calls_note("in_label_hangup", phone.HangUp().get_sensitive())
    $ _calls_later(0.7, Function(_calls_snap, "calls-in-call"), Function(_calls_note_state, "in_label_state"))
    e "Hey! It's Eileen. Just calling to say hi.{w=1.0}{nw}"
    $ _calls_note("in_label_overlay", renpy.get_screen("phone_calls_active") is not None)
    $ _calls_note("eileen_label_done", True)
    return

label _test_calls_declined:
    $ _calls_note("declined_label", True)
    $ _calls_note("declined_in_call", phone.in_call())
    return

label _test_calls_lucy_call:
    $ _calls_note("lucy_in_call", phone.in_call())
    $ _calls_note("lucy_phone_open", phone.is_open())
    l "Hi! You called?{w=0.3}{nw}"
    $ _calls_note("lucy_overlay", renpy.get_screen("phone_calls_active") is not None)
    $ _calls_note("lucy_label_done", True)
    return


label test_calls_model:
    # The runner works inside the splashscreen, which hides overlay screens
    # such as the in-call pill; a game shows them.
    $ suppress_overlay = False
    $ expect(phone.get_app("calls") is not None, "calls app is registered")
    $ expect_eq(phone.caller_key("eileen"), "eileen", "contact ids are kept")
    $ expect_eq(phone.caller_key(eileen), "eileen", "contacts become ids")
    $ expect_eq(phone.caller_key("555 0199"), "lucy", "numbers of contacts resolve to the contact")
    $ expect_eq(phone.caller_key("555-9999"), "555-9999", "unknown numbers stay numbers")
    $ expect_eq(phone.caller_name("555-9999"), "555-9999", "unknown callers show their number")

    $ a = phone.log_call("max", "outgoing", duration="1:00", time="09:00")
    $ b = phone.log_call("555-9999", "incoming")
    $ expect(a.uid != b.uid, "records get distinct uids")
    $ expect_eq([r.uid for r in phone.call_log()], [b.uid, a.uid], "call_log is newest first")
    $ expect_eq([r.uid for r in phone.call_log("max")], [a.uid], "call_log filters by caller")
    $ expect_eq(phone.call_description(a), "Outgoing · 1:00", "description with duration")
    $ expect_eq(phone.get_call_record(b.uid), b, "records are found by uid")
    $ expect_eq(phone.format_duration(65), "1:05", "durations")
    $ expect_eq(phone.format_duration(3725), "1:02:05", "long durations")

    # start_call / end_call from the script.
    $ rec = phone.start_call("lucy")
    $ expect(phone.in_call(), "start_call starts a call")
    $ expect_eq(rec.direction, "outgoing", "script calls are outgoing")
    $ expect("phone_calls_active" in config.overlay_screens, "the in-call pill is an overlay screen")
    $ wait(0.1)
    $ expect(renpy.get_screen("phone_calls_active") is not None, "the in-call pill shows")
    $ expect(phone.HangUp().get_sensitive(), "hang up is available without a label")
    python:
        from renpy.compat.pickle import dumps, loads
        s = loads(dumps(phone.calls_state))
        expect_eq([(r.uid, r.who, r.direction) for r in s.log], [(r.uid, r.who, r.direction) for r in phone.calls_state.log], "call log pickles")
        expect_eq(s.active.who, "lucy", "active call pickles")
    $ phone.end_call(duration="4:20")
    $ expect(not phone.in_call(), "end_call ends the call")
    $ expect_eq(rec.duration, "4:20", "end_call records the duration")

    $ phone.start_call("eileen")
    $ phone.end_call()
    $ expect_eq(phone.call_log()[0].duration, "0:00", "measured duration")

    $ phone.clear_call_log()
    $ expect_eq(phone.call_log(), [], "clear_call_log")
    $ expect_eq(phone.call_contacts(), [eileen], "only known contacts are listed")

    # Full-display backgrounds for the call screens.
    $ expect(phone.screen_background("phone_calls_incoming") is not None, "incoming call screen has a background")
    $ expect(phone.screen_background("phone_calls_outgoing") is not None, "outgoing call screen has a background")
    $ expect(phone.screen_background("phone_calls") is None, "normal screens have none")
    $ suppress_overlay = True
    return


label test_calls_missed_badge:
    $ expect(not max_.known, "max starts unknown")
    $ phone.missed_call("max")
    $ expect(max_.known, "a missed call makes the caller known")
    $ expect_eq(phone.get_app("calls").badge(), 1, "missed call badge")
    $ expect_eq(phone.call_log()[0].direction, "missed", "missed call is logged")
    $ expect(renpy.get_screen("phone_notification") is not None, "missed call notification")
    $ shot("calls-missed-notification")
    $ renpy.hide_screen("phone_notification")
    $ phone.missed_call("555-0123")
    $ renpy.hide_screen("phone_notification")
    $ expect_eq(phone.total_badges(), 2, "badges add up")
    $ phone.show()
    $ shot("calls-home-badge")

    # Opening on another tab keeps the badge; viewing Recents clears it.
    $ phone.Launch("calls", tab="contacts")()
    $ expect_eq(phone.missed_calls(), 2, "the Contacts tab keeps the badge")
    $ phone.CallsTab("recents")()
    $ expect_eq(phone.missed_calls(), 0, "the Recents tab clears the badge")

    $ phone.missed_call("lucy")
    $ phone.CallsTab("keypad")()
    $ phone.state.replace("phone_calls", tab="recents")
    $ wait(0.4)
    $ expect_eq(phone.missed_calls(), 0, "Recents on screen clears the badge")

    $ phone.missed_call("eileen")
    $ phone.close()
    $ phone.show("calls")
    $ expect_eq(phone.missed_calls(), 0, "launching the app clears the badge")
    $ shot("calls-recents-missed")
    $ phone.close()
    return


label test_calls_incoming_label:
    # The runner works inside the splashscreen, which hides overlay screens
    # such as the in-call pill; a game shows them.
    $ suppress_overlay = False
    $ _calls_seen.clear()
    $ _calls_later(0.9, Function(_calls_note_state, "ringing"), Function(_calls_snap, "calls-incoming"), Return("accept"))
    # The call label runs in the story; the statement after this one runs
    # once it returns, and this one does not run again.
    $ _calls_count("ring_runs"); phone.incoming_call("eileen", label="_test_calls_eileen_call")
    $ _calls_count("after_runs")
    $ _calls_note("after_in_call", phone.in_call())

    $ expect_eq(_calls_seen.get("ring_runs"), 1, "the incoming_call statement runs once")
    $ expect_eq(_calls_seen.get("after_runs"), 1, "the statement after incoming_call runs once")
    $ expect_eq(_calls_seen.get("ringing", {}).get("ringing"), "eileen", "ringing while waiting")
    $ expect(_calls_seen.get("ringing", {}).get("incoming_shown"), "the phone shows the incoming call screen")
    $ expect(_calls_seen.get("in_label_in_call"), "calls_state.active is set in the label")
    $ expect(_calls_seen.get("in_label_label_flag"), "the active call knows a label runs")
    $ expect(not _calls_seen.get("in_label_hangup", True), "hang up is hidden while a label runs")
    $ expect(not _calls_seen.get("in_label_state", {}).get("open", True), "the phone is closed during the call")
    $ expect(_calls_seen.get("in_label_overlay"), "the pill shows during the call")
    $ expect(_calls_seen.get("eileen_label_done"), "the call label ran its dialogue")
    $ expect(not _calls_seen.get("after_in_call", True), "calls_state.active is cleared after the label")
    $ expect(not phone.is_open(), "the phone is closed after the call")
    $ expect(phone.calls_state.ringing is None, "no longer ringing")
    $ rec = phone.call_log()[0]
    $ expect_eq((rec.who, rec.direction), ("eileen", "incoming"), "accepted call is logged")
    $ expect(rec.duration is not None, "accepted call has a duration")

    # Without labels, the return value tells what happened.
    $ _calls_later(0.4, Return("accept"))
    $ answered = phone.incoming_call("eileen")
    $ expect(answered is True, "accepting returns True")
    $ phone.end_call()
    $ suppress_overlay = True
    return


label _test_calls_save_call:
    e "Line before saving.{w=0.2}{nw}"
    python:
        if not persistent._calls_test_loaded:
            persistent._calls_test_loaded = True
            renpy.save("_calls_test_save")
            _calls_note("not_reloaded", True)
            renpy.load("_calls_test_save")
    $ wait(0.2)
    $ _calls_note("loaded_in_call", bool(phone.in_call() and phone.active_call().label))
    $ _calls_note("loaded_pill", renpy.get_screen("phone_calls_active") is not None)
    $ _calls_note("loaded_label", True)
    $ shot("calls-after-load")
    return


label test_calls_save_mid_call:
    # The runner works inside the splashscreen, which hides overlay screens
    # such as the in-call pill; a game shows them.
    $ suppress_overlay = False
    # A save made inside a call label loads back into the call label.
    $ _calls_seen.clear()
    $ persistent._calls_test_loaded = False
    $ _calls_later(0.4, Return("accept"))
    $ _calls_count("ring_runs"); phone.incoming_call("lucy", label="_test_calls_save_call")
    $ _calls_count("after_runs")
    $ renpy.unlink_save("_calls_test_save")
    $ expect(persistent._calls_test_loaded, "the save was loaded")
    $ persistent._calls_test_loaded = None
    $ expect(not _calls_seen.get("not_reloaded"), "the game state comes from the save")
    $ expect(_calls_seen.get("loaded_label"), "the call label carries on after loading")
    $ expect(_calls_seen.get("loaded_in_call"), "the call is active after loading")
    $ expect(_calls_seen.get("loaded_pill"), "the pill shows after loading")
    $ expect_eq(_calls_seen.get("ring_runs"), 1, "loading does not ring again")
    $ expect_eq(_calls_seen.get("after_runs"), 1, "the story resumes once after the call")
    $ expect(not phone.in_call(), "the call ends when the label returns")
    $ suppress_overlay = True
    return


label test_calls_incoming_decline:
    $ _calls_seen.clear()
    # The nav bar's Back button while ringing still shows the call.
    $ _calls_later(0.3, phone.Back())
    $ _calls_later(0.6, Function(_calls_note_state, "back"))
    $ _calls_later(0.9, Return("decline"))
    $ _calls_count("ring_runs"); phone.incoming_call("max", label="_test_calls_eileen_call", decline_label="_test_calls_declined")
    $ _calls_count("after_runs")
    $ expect_eq((_calls_seen.get("ring_runs"), _calls_seen.get("after_runs")), (1, 1), "the story resumes once after decline_label")
    $ expect_eq(_calls_seen.get("back", {}).get("current"), ("phone_calls", {}), "Back while ringing goes to the app root")
    $ expect_eq(_calls_seen.get("back", {}).get("ringing"), "max", "still ringing after Back")
    $ expect(_calls_seen.get("declined_label"), "decline_label is called")
    $ expect(not _calls_seen.get("declined_in_call", True), "no call during decline_label")
    $ expect(not _calls_seen.get("eileen_label_done"), "the call label does not run")
    $ expect_eq(phone.call_log()[0].direction, "declined", "declined call is logged")
    $ expect(max_.known, "a declined caller becomes known")

    # Closing the phone while it rings declines too.
    $ _calls_later(0.5, phone.Close())
    $ answered = phone.incoming_call("555-0123")
    $ expect(answered is False, "closing the phone declines")
    $ expect_eq((phone.call_log()[0].who, phone.call_log()[0].direction), ("555-0123", "declined"), "unknown caller logged")
    return


label test_calls_incoming_no_label:
    # The runner works inside the splashscreen, which hides overlay screens
    # such as the in-call pill; a game shows them.
    $ suppress_overlay = False
    $ _calls_seen.clear()
    # Without can_decline, closing the phone keeps it ringing.
    $ _calls_later(0.4, phone.Close())
    $ _calls_later(1.2, Function(_calls_note_state, "reopened"), Function(_calls_snap, "calls-incoming-nodecline"), Return("accept"))
    $ answered = phone.incoming_call("555-0123", can_decline=False)
    $ expect(answered is True, "accepted")
    $ expect(_calls_seen.get("reopened", {}).get("incoming_shown"), "closing does not decline when can_decline is False")
    $ expect(phone.in_call(), "without a label the call stays active")
    $ expect(phone.HangUp().get_sensitive(), "hang up is shown")
    $ _calls_later(0.6, Function(_calls_snap, "calls-pill-dialogue"))
    "Unknown caller" "Hello? Who is this?{w=1.0}{nw}"
    $ shot("calls-pill")
    $ phone.HangUp()()
    $ expect(not phone.in_call(), "hang up ends the call")
    $ expect(phone.call_log()[0].duration is not None, "duration is recorded")

    # Dark theme screenshots of the call screens.
    $ phone.set_theme("dark")
    $ _calls_later(0.9, Function(_calls_snap, "calls-incoming-dark"), Return("accept"))
    $ phone.incoming_call("lucy")
    $ shot("calls-pill-dark")
    $ phone.end_call()
    $ phone.set_theme("light")
    $ suppress_overlay = True
    return


label test_calls_outgoing_open:
    # The runner works inside the splashscreen, which hides overlay screens
    # such as the in-call pill; a game shows them.
    $ suppress_overlay = False
    # Dialing from phone.open(): the call label runs in the story, then the
    # phone.open() statement runs again and shows Recents; the story goes on
    # when the player closes the phone.
    $ _calls_seen.clear()
    $ phone.add_contact("lucy")
    $ phone.set_call_label("lucy", "_test_calls_lucy_call")
    show screen _calls_call_driver
    $ _calls_count("open_runs"); phone.open("calls", "phone_calls_contact", who="lucy")
    $ _calls_count("after_runs")
    hide screen _calls_call_driver

    $ expect(_calls_seen.get("lucy_in_call"), "the call is active during the label")
    $ expect(not _calls_seen.get("lucy_phone_open", True), "the phone is hidden during the call")
    $ expect(_calls_seen.get("lucy_overlay"), "the pill shows during the call")
    $ expect(_calls_seen.get("lucy_label_done"), "the call label ran")
    $ expect_eq(_calls_seen.get("open_runs"), 2, "the phone.open() statement runs again after the call")
    $ expect_eq(_calls_seen.get("after", {}).get("current"), ("phone_calls", {}), "the phone reopens on Recents")
    $ expect(_calls_seen.get("after", {}).get("open"), "the phone is open again after the call")
    $ expect_eq(_calls_seen.get("after_runs"), 1, "the story resumes once after the phone is closed")
    $ expect(phone._open_next is None, "the reopen request was used up")
    $ expect(not phone.in_call(), "call ended")
    $ rec = phone.call_log()[0]
    $ expect_eq((rec.who, rec.direction), ("lucy", "outgoing"), "outgoing call logged")
    $ expect(rec.duration is not None, "answered outgoing call has a duration")
    $ suppress_overlay = True
    return


label test_calls_outgoing_show:
    # The runner works inside the splashscreen, which hides overlay screens
    # such as the in-call pill; a game shows them.
    $ suppress_overlay = False
    # Dialing from phone.show() during a say statement: the line is
    # interrupted by the call and shown again afterwards, with the phone
    # open on Recents.
    $ _calls_seen.clear()
    $ phone.add_contact("lucy")
    $ phone.set_call_label("lucy", "_test_calls_lucy_call")
    $ phone.show("calls", "phone_calls_contact", who="lucy")
    show screen _calls_call_driver
    _calls_narrator "The story waits while you use the phone.{w=2.0}{nw}"
    $ _calls_count("after_runs")
    hide screen _calls_call_driver
    $ expect(_calls_seen.get("lucy_label_done"), "the call label ran")
    $ expect(not _calls_seen.get("lucy_phone_open", True), "the phone is hidden during the call")
    $ expect_eq(_calls_seen.get("say_runs"), 2, "the interrupted line is shown again")
    $ expect_eq(_calls_seen.get("after", {}).get("current"), ("phone_calls", {}), "the phone is back on Recents")
    $ expect(_calls_seen.get("after", {}).get("open"), "the phone is open again after the call")
    $ expect_eq(_calls_seen.get("after_runs"), 1, "the story resumes once")
    $ expect(not phone.in_call(), "call ended")
    $ phone.close()
    $ suppress_overlay = True
    return


label test_calls_no_answer:
    $ phone.add_contact("max")
    $ phone.show("calls", "phone_calls_contact", who="max")
    $ phone.CallContact("max")()
    $ expect_eq(phone.state.current(), ("phone_calls_outgoing", {"who": "max", "uid": phone.call_log()[0].uid}), "no label: the outgoing screen shows")
    $ expect_eq((phone.call_log()[0].who, phone.call_log()[0].direction, phone.call_log()[0].duration), ("max", "outgoing", None), "unanswered call logged")
    $ shot("calls-outgoing")
    $ wait(max(0.1, phone.OUTGOING_NO_ANSWER + 0.1 - phone.outgoing_elapsed(phone.call_log()[0].uid)))
    $ expect(phone.outgoing_elapsed(phone.call_log()[0].uid) >= phone.OUTGOING_NO_ANSWER, "no answer after a moment")
    $ shot("calls-no-answer")
    $ wait(1.6)
    $ expect_eq(phone.state.current(), ("phone_calls_contact", {"who": "max"}), "the outgoing screen closes by itself")
    $ phone.close()
    return


label test_calls_keypad:
    $ phone.add_contact("lucy")
    $ phone.show("calls", tab="keypad")
    $ expect(not phone.DialNumber().get_sensitive(), "nothing to dial yet")
    python:
        for k in "5550199":
            phone.KeypadPress(k)()
    $ expect_eq(phone.calls_state.dialed, "5550199", "keypad input")
    $ expect_eq(phone.contact_by_number(phone.calls_state.dialed), lucy, "typed number matches a contact")
    $ shot("calls-keypad")
    $ phone.KeypadDelete()()
    $ expect_eq(phone.calls_state.dialed, "555019", "delete")
    $ phone.KeypadPress("9")()
    $ phone.DialNumber()()
    $ expect_eq(phone.calls_state.dialed, "", "dialing clears the keypad")
    $ expect_eq(phone.call_log()[0].who, "lucy", "keypad dials the matching contact")
    $ expect_eq(phone.state.current()[0], "phone_calls_outgoing", "lucy has no label: no answer")
    $ phone.Back()()
    $ phone.KeypadPress("1")()
    $ phone.KeypadPress("2")()
    $ phone.DialNumber()()
    $ expect_eq(phone.call_log()[0].who, "12", "unknown numbers are logged as numbers")
    $ phone.close()
    return


init python:
    def _calls_demo_step():
        """Plays the demo: answers Eileen, then calls Lucy back from Recents."""
        s = _calls_seen
        if phone.calls_state.ringing is not None:
            return "accept"
        if phone.is_showing("phone_calls") and not s.get("demo_called"):
            s["demo_called"] = True
            s["demo_recents"] = [(r.who, r.direction) for r in phone.call_log()]
            phone.CallContact("lucy")()  # ends the phone.open() statement
        if phone.is_open() and s.get("demo_called") and not phone.in_call():
            s["demo_after_call"] = phone.state.current()
            return phone.Close()()
        return None

screen _calls_demo_driver():
    zorder 10001
    timer 0.3 repeat True action Function(_calls_demo_step)


label test_calls_demo:
    # The runner works inside the splashscreen, which hides overlay screens
    # such as the in-call pill; a game shows them.
    $ suppress_overlay = False
    # Runs the demo with auto-forward on and a driver pressing the phone
    # buttons.
    $ _calls_seen.clear()
    $ _preferences.afm_enable = True
    $ _preferences.afm_time = 0.5
    show screen _calls_demo_driver
    call demo_calls
    hide screen _calls_demo_driver
    $ _preferences.afm_enable = False

    $ expect_eq(phone.call_log("eileen")[0].direction, "incoming", "Eileen's call was answered")
    $ expect_eq(phone.call_log("max")[0].direction, "missed", "Max's call was missed")
    $ expect_eq(_calls_seen.get("demo_recents", [])[:3], [("max", "missed"), ("eileen", "incoming"), ("lucy", "missed")], "Recents in the demo")
    $ expect_eq((phone.call_log()[0].who, phone.call_log()[0].direction), ("lucy", "outgoing"), "Lucy was called back")
    $ expect(phone.call_log()[0].duration is not None, "Lucy answered")
    $ expect_eq(_calls_seen.get("demo_after_call"), ("phone_calls", {}), "back on Recents after the call")
    $ expect(not phone.in_call(), "no call left active")
    $ suppress_overlay = True
    return


label test_calls_screens:
    # A populated log, in both themes.
    $ phone.add_contact("lucy")
    $ phone.add_contact("max")
    $ phone.log_call("lucy", "outgoing", duration="12:04", time="Mon")
    $ phone.log_call("555-0123", "incoming", duration="0:42", time="Tue")
    $ phone.log_call("max", "declined", time="09:12")
    $ phone.log_call("eileen", "incoming", duration="3:17", time="11:40")
    $ phone.log_call("max", "missed", time="12:05")
    $ phone.show("calls")
    $ shot("calls-recents")
    $ phone.CallsTab("contacts")()
    $ shot("calls-contacts")
    $ phone.Navigate("phone_calls_contact", who="max")()
    $ shot("calls-contact")
    $ phone.close()
    $ phone.show("calls", tab="keypad")
    $ shot("calls-keypad-empty")

    $ phone.set_theme("dark")
    $ phone.show("calls")
    $ shot("calls-recents-dark")
    $ phone.CallsTab("contacts")()
    $ shot("calls-contacts-dark")
    $ phone.Navigate("phone_calls_contact", who="eileen")()
    $ shot("calls-contact-dark")
    $ phone.CallsTab("keypad")()
    $ phone.KeypadPress("5")()
    $ shot("calls-keypad-dark")
    $ phone.close()
    $ phone.clear_call_log()
    $ phone.show("calls")
    $ shot("calls-empty-dark")
    $ phone.close()
    $ phone.set_theme("light")
    return
