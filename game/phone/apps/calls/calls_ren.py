"""renpy
init -920 python in phone:
"""

# Phone app: call log, incoming and outgoing calls.
#
# A call is a story scene: what is said during a call is ordinary Ren'Py
# dialogue in a label.
#
#     $ phone.incoming_call("eileen", label="eileen_call")
#
#     if phone.incoming_call("max", can_decline=False):
#         m "Hey, got a minute?"
#         $ phone.end_call()
#
#     $ phone.missed_call("lucy")
#
# Call labels given to incoming_call() and Contact(call_label=...) run in a
# nested context, like Ren'Py's own menus: when the label returns, the story
# carries on exactly where it was (after the incoming_call() statement, or
# with the phone still open on the Recents tab after the player phoned
# someone). Variables changed by the label are kept; images it shows are
# discarded when the call ends. As in any nested context, rollback is not
# available inside such a call, and a save made during it is a save of the
# top-level story: loading it goes back to the statement the call started
# from (the ringing, or the phone before the player dialed).
# A call label must end with `return`.
#
# Calls started without a label (incoming_call() without `label`, or
# start_call()) run in the story itself, so rollback and saving work as
# usual; end them with phone.end_call().

import time as _calls_time

cfg.sounds.setdefault("ringtone", None)  # loops while an incoming call rings
cfg.sounds.setdefault("dialing", None)  # played when the player places a call

# The call screens are dark in both themes, like a real phone.
for _k, _v in (("call_bg", "#14161b"), ("call_text", "#ffffff"), ("call_subtext", "#b8bcc6")):
    cfg.themes["light"].setdefault(_k, _v)
    cfg.themes["dark"].setdefault(_k, _v)

CALL_DIRECTIONS = ("incoming", "outgoing", "missed", "declined")


class CallRecord(object):
    """One line of the call log.

    `who` is a contact id, or the raw number of an unknown caller.
    `direction` is "incoming", "outgoing", "missed" or "declined".
    `duration` is a label such as "2:05", or None (not answered).
    `time` is the status bar clock when the call happened.
    """

    def __init__(self, uid, who, direction, duration=None, time=None):
        self.uid = uid
        self.who = who
        self.direction = direction
        self.duration = duration
        self.time = time

    def __repr__(self):
        return "<CallRecord {} {} {}>".format(self.uid, self.who, self.direction)


class ActiveCall(object):
    """The call in progress. `label` is True while a call label runs."""

    def __init__(self, who, uid, label=False):
        self.who = who
        self.uid = uid
        self.label = label
        self.started = _calls_time.time()


class CallsState(object):
    def __init__(self):
        self.log = []  # CallRecord, oldest first
        self.active = None  # ActiveCall or None
        self.unseen_missed = 0  # badge; cleared when Recents is viewed
        self.ringing = None  # caller key while an incoming call rings
        self.ringing_can_decline = True
        self.dialed = ""  # keypad display


# Callers --------------------------------------------------------------------

def _digits(number):
    return "".join(ch for ch in (number or "") if ch.isdigit())


def contact_by_number(number):
    """The contact whose number matches `number` (digits only), or None."""
    d = _digits(number)
    if not d:
        return None
    for c in contacts.values():
        if c.number and _digits(c.number) == d:
            return c
    return None


def caller_key(who):
    """A contact id for contacts (given as Contact, id or their number), else the raw number."""
    if isinstance(who, Contact):
        return who.id
    if who in contacts:
        return who
    c = contact_by_number(who)
    if c is not None:
        return c.id
    return who


def is_contact_key(key):
    return key in contacts


def caller_name(key):
    if is_contact_key(key):
        return contact(key).name
    return key


def caller_number(key):
    """The number to show under the name ("" if unknown)."""
    if is_contact_key(key):
        return contact(key).number or ""
    return key


def caller_avatar(key, size):
    if is_contact_key(key):
        return avatar(key, size)
    size = int(size)
    return Fixed(
        circle("#8e8e93", size),
        Text("☏", font=GLYPH_FONT, size=int(size * 0.5), color="#ffffff", xalign=0.5, yalign=0.5),
        xysize=(size, size),
    )


# Call log -------------------------------------------------------------------

def log_call(who, direction, duration=None, time=None):
    """Adds a call to the log (e.g. for calls that happened off screen).

    Returns the CallRecord. `time` defaults to the phone clock.
    """
    if direction not in CALL_DIRECTIONS:
        raise Exception("phone.log_call: direction must be one of {!r}.".format(CALL_DIRECTIONS))
    key = caller_key(who)
    rec = CallRecord(state.next_uid(), key, direction, duration, time if time is not None else clock_text())
    calls_state.log.append(rec)
    return rec


def call_log(who=None):
    """Call records, newest first; only those with `who` if given."""
    rv = list(reversed(calls_state.log))
    if who is not None:
        key = caller_key(who)
        rv = [r for r in rv if r.who == key]
    return rv


def get_call_record(uid):
    for r in calls_state.log:
        if r.uid == uid:
            return r
    return None


def clear_call_log():
    calls_state.log = []
    calls_state.unseen_missed = 0


def missed_calls():
    """Missed calls the player has not seen yet (the app badge)."""
    return calls_state.unseen_missed


def mark_calls_seen():
    calls_state.unseen_missed = 0


def missed_call(who):
    """Logs a missed call from `who` and shows a notification."""
    key = caller_key(who)
    if is_contact_key(key):
        add_contact(key)
    rec = log_call(key, "missed")
    calls_state.unseen_missed += 1
    notify(caller_name(key), store.__("Missed call"), app_id="calls")
    return rec


def call_contacts():
    """Known contacts in alphabetical order (the Contacts tab)."""
    return sorted(known_contacts(), key=lambda c: c.name.lower())


# Arrows that DejaVu Sans draws as plain glyphs (not color emoji).
CALL_GLYPHS = {"incoming": "⬋", "outgoing": "⬈", "missed": "⬋", "declined": "⬋"}

_CALL_WORDS = {
    "incoming": store._("Incoming"),
    "outgoing": store._("Outgoing"),
    "missed": store._("Missed"),
    "declined": store._("Declined"),
}

# (key, letters) of the keypad, row by row.
KEYPAD = [
    ("1", ""), ("2", "ABC"), ("3", "DEF"),
    ("4", "GHI"), ("5", "JKL"), ("6", "MNO"),
    ("7", "PQRS"), ("8", "TUV"), ("9", "WXYZ"),
    ("*", ""), ("0", "+"), ("#", ""),
]


def call_glyph(direction):
    return CALL_GLYPHS.get(direction, "")


def call_description(rec):
    """E.g. "Incoming · 2:05" or "Missed"."""
    rv = store.__(_CALL_WORDS.get(rec.direction, rec.direction))
    if rec.duration:
        rv += " · " + rec.duration
    return rv


def format_duration(seconds):
    seconds = max(0, int(seconds))
    if seconds >= 3600:
        return "{}:{:02d}:{:02d}".format(seconds // 3600, (seconds // 60) % 60, seconds % 60)
    return "{}:{:02d}".format(seconds // 60, seconds % 60)


# Active call ----------------------------------------------------------------

def in_call():
    return calls_state.active is not None


def active_call():
    """The ActiveCall in progress, or None."""
    return calls_state.active


def _begin_call(key, uid, label=False):
    calls_state.active = ActiveCall(key, uid, label)
    renpy.show_screen("phone_calls_active", _layer=cfg.layer, _zorder=cfg.zorder - 1)


def start_call(who):
    """Starts a call with `who` from the script (logged as outgoing).

    The in-call overlay stays on screen while the dialogue goes on; end the
    call with phone.end_call(). Returns the CallRecord.
    """
    if in_call():
        end_call()
    key = caller_key(who)
    rec = log_call(key, "outgoing")
    _begin_call(key, rec.uid)
    return rec


def end_call(duration=None):
    """Ends the call in progress and records its length.

    `duration` overrides the measured length, e.g. "12:40".
    """
    a = calls_state.active
    if a is None:
        return
    rec = get_call_record(a.uid)
    if rec is not None:
        if duration is None:
            duration = format_duration(_calls_time.time() - a.started)
        rec.duration = duration
    calls_state.active = None
    if renpy.get_screen("phone_calls_active", layer=cfg.layer) is not None:
        renpy.hide_screen("phone_calls_active", layer=cfg.layer)


def _calls_after_load():
    # The overlay timer restarts when a game is loaded; keep the duration
    # measured the same way.
    s = globals().get("calls_state")
    if s is not None and s.active is not None:
        s.active.started = _calls_time.time()


if _calls_after_load not in store.config.after_load_callbacks:
    store.config.after_load_callbacks.append(_calls_after_load)


def _call_timer_text(st, at):
    return Text(format_duration(st), style="phone_calls_active_timer"), 1.0 - (st % 1.0)


def _nested(label, *args):
    """Runs a call label in a nested context and returns when it does."""
    global _called
    # The phone may be waiting in phone.open() outside; inside the call it
    # starts closed, and phone.Close() there must only hide it.
    saved = _called
    _called = False
    try:
        renpy.call_in_new_context(label, *args)
    finally:
        _called = saved


def _run_call_label(key, uid, label):
    try:
        _nested("phone_calls_session", key, uid, label)
    finally:
        if in_call():
            end_call()


# Ringing --------------------------------------------------------------------

def _ring_start():
    fn = cfg.sounds.get("ringtone")
    if fn and store.persistent._phone_sounds is not False:
        renpy.music.play(fn, channel=cfg.channel, loop=True)


def _ring_stop():
    if cfg.sounds.get("ringtone") and renpy.music.is_playing(channel=cfg.channel):
        renpy.music.stop(channel=cfg.channel)


def incoming_call(who, label=None, decline_label=None, can_decline=True, ring=True):
    """Rings the phone and waits for the player to answer or decline.

    `label`
        Called when the player answers; the call ends when it returns.
        Without it the call stays active, so the script can go on with the
        conversation and then `$ phone.end_call()`.
    `decline_label`
        Called when the player declines.
    `can_decline`
        False hides the decline button.
    `ring`
        False keeps the ringtone (cfg.sounds["ringtone"]) silent.

    Returns True if the player answered.
    """
    global _called

    key = caller_key(who)
    if is_contact_key(key):
        add_contact(key)
    if in_call():
        end_call()

    s = calls_state
    s.ringing = key
    s.ringing_can_decline = bool(can_decline)
    if ring:
        _ring_start()

    background_click = cfg.close_on_background_click
    cfg.close_on_background_click = False
    saved_called = _called
    result = None
    try:
        while True:
            state.launch("calls", "phone_calls_incoming", who=key, can_decline=bool(can_decline))
            # Makes phone.Close() end the interaction instead of hiding the
            # called screen.
            _called = True
            result = renpy.call_screen("phone", _layer=cfg.layer, _zorder=cfg.zorder)
            if result in ("accept", "decline"):
                break
            # The player closed the phone: that declines, unless they can't.
            if can_decline:
                result = "decline"
                break
    finally:
        _called = saved_called
        cfg.close_on_background_click = background_click
        s.ringing = None
        if ring:
            _ring_stop()
        state.home()

    if result == "accept":
        rec = log_call(key, "incoming")
        if label:
            _run_call_label(key, rec.uid, label)
        else:
            _begin_call(key, rec.uid)
        return True

    log_call(key, "declined")
    if decline_label:
        _nested(decline_label)
    return False


# Outgoing calls -------------------------------------------------------------

def can_dial():
    return calls_state.active is None and calls_state.ringing is None


def dial(who):
    """The player phones `who` (a contact or a number).

    If the contact has a call label (Contact.call_label, or one set with
    phone.set_call_label), it runs with the in-call overlay and the phone
    then shows the Recents tab. Otherwise the phone shows a call that is not
    answered. Meant to be run from the phone (see phone.CallContact).
    """
    key = caller_key(who)
    label = contact(key).label if is_contact_key(key) else None
    rec = log_call(key, "outgoing")
    play_sound("dialing")
    if label and renpy.has_label(label):
        _run_call_label(key, rec.uid, label)
        state.launch("calls")
    else:
        _outgoing_started[rec.uid] = _calls_time.time()
        state.navigate("phone_calls_outgoing", who=key, uid=rec.uid)


# The unanswered outgoing call screen: "calling…", then "No answer", then it
# closes. Timed with the wall clock, as screen timers restart whenever the
# screen is updated.
OUTGOING_NO_ANSWER = 1.3
OUTGOING_CLOSE = 2.6
_outgoing_started = {}  # record uid -> time.time(); not saved


def outgoing_elapsed(uid):
    return _calls_time.time() - _outgoing_started.setdefault(uid, _calls_time.time())


class _OutgoingTick(Action, DictEquality):
    def __init__(self, uid):
        self.uid = uid

    def __call__(self):
        screen, kwargs = state.current()
        if screen != "phone_calls_outgoing" or kwargs.get("uid") != self.uid:
            return
        if outgoing_elapsed(self.uid) >= OUTGOING_CLOSE:
            _outgoing_started.pop(self.uid, None)
            state.back()
            mutated()
        else:
            renpy.restart_interaction()


# Actions --------------------------------------------------------------------

class CallContact(PhoneAction):
    """Phones a contact (or number) from a screen: calls its call label."""

    def __init__(self, who):
        self.who = caller_key(who)

    def get_sensitive(self):
        return can_dial()

    def run(self):
        dial(self.who)


class DialNumber(PhoneAction):
    """Calls the number typed on the keypad (or the given one)."""

    def __init__(self, number=None):
        self.number = number

    def get_sensitive(self):
        return can_dial() and bool(self.number or calls_state.dialed)

    def run(self):
        number = self.number or calls_state.dialed
        calls_state.dialed = ""
        dial(number)


class KeypadPress(PhoneAction):
    def __init__(self, key):
        self.key = key

    def run(self):
        play_sound("tap")
        if len(calls_state.dialed) < 15:
            calls_state.dialed += self.key


class KeypadDelete(PhoneAction):
    def get_sensitive(self):
        return bool(calls_state.dialed)

    def run(self):
        calls_state.dialed = calls_state.dialed[:-1]


class CallsTab(PhoneAction):
    """Switches the tab of the Phone app ("recents", "contacts", "keypad")."""

    def __init__(self, tab):
        self.tab = tab

    def run(self):
        state.replace("phone_calls", tab=self.tab)
        if self.tab == "recents":
            mark_calls_seen()


class CallsSeen(PhoneAction):
    def run(self):
        mark_calls_seen()


class ClearCallLog(PhoneAction):
    def run(self):
        clear_call_log()


class HangUp(PhoneAction):
    """Ends a call started without a label (the overlay's hang-up button)."""

    def get_sensitive(self):
        a = calls_state.active
        return a is not None and not a.label

    def run(self):
        end_call()


"""renpy
default phone.calls_state = phone.CallsState()
"""
