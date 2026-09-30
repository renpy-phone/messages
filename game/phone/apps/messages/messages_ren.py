"""renpy
init -920 python in phone:
"""

# Messages app: model and public API.
#
# Conversations are built with the fluent `phone.Chat` builder and sent from
# the script:
#
#     define eileen_hello = phone.Chat("eileen").say("Hey!").say("Free tonight?").choice(
#         phone.Reply("Sure!", then=phone.Chat("eileen").say("Great, 8pm.").set("dinner", True)),
#         phone.Reply("Sorry, busy.", then=["Another time then."]),
#     )
#
#     label chapter_2:
#         $ eileen_hello.send()
#         $ phone.open_chat("eileen")
#
# A Chat is a template: building it touches no saved state, so it is safe to
# `define` at init time, and every send() queues a fresh copy. Messages are
# delivered in order up to and including the first one that offers a choice;
# the conversation then waits for the player's answer. Choosing a reply adds
# the player's message, runs the reply's effects and puts its follow-up at the
# front of the queue. Effects added with .set() / .add() / .effect() run when
# playback reaches them, not when the chat is sent.

import store  # pyright: ignore[reportMissingImports]

cfg.messages_typing_delay = 0.8  # seconds per message while a chat is on screen; 0 = instant
cfg.messages_max_rendered = 100  # a conversation screen shows at most this many entries
cfg.sounds.setdefault("message", None)

require_art(
    "messages/bubble_in", "messages/bubble_in_tail",
    "messages/bubble_out", "messages/bubble_out_tail",
    "messages/typing_dot", "messages/reply", "messages/composer",
    "messages/thumb_mask", "messages/thumb_mask_small", "messages/group_ring",
    "messages/back", "common/avatar_mask",
)

THREAD_SCREEN = "phone_messages_thread"

# Entry kinds.
TEXT = "text"
IMAGE = "image"
ME = "me"
NOTE = "note"
# Pending-only kinds: never shown in the log.
_PROMPT = "prompt"
_EFFECT = "effect"
_MESSAGE_KINDS = (TEXT, IMAGE, ME, NOTE)


# Groups ----------------------------------------------------------------------

groups = {}  # id -> Group


class Group(python_object):
    """A group chat. Static: create it with `define` and phone.group()."""

    def __init__(self, id, name, members, avatar=None):
        if id in groups and groups[id] is not self:
            raise Exception("phone.group id {!r} is defined twice.".format(id))
        self.id = id
        self._name = name
        self.members = [contact_id(m) for m in members]
        self.avatar = avatar
        groups[id] = self

    def __reduce__(self):
        return (_group_by_id, (self.id,))

    def __repr__(self):
        return "<phone.Group {}>".format(self.id)

    @property
    def name(self):
        return renpy.substitute(self._name)


def _group_by_id(gid):
    rv = groups.get(gid)
    if rv is None:
        # A save refers to a group the current scripts no longer define.
        rv = python_object.__new__(Group)
        rv.__dict__.update(id=gid, _name=gid, members=[], avatar=None)
    return rv


def group(id, name, members, avatar=None):
    """Defines a group chat: `define crew = phone.group("crew", "Crew", [lucy, max_])`."""
    init_only("phone.group()")
    return Group(id, name, members, avatar)


def thread_id(who):
    """The conversation id for a Contact, a Group, or an id string."""
    if isinstance(who, Group):
        return who.id
    return contact_id(who)


def is_group(tid):
    return tid in groups


def thread_title(tid):
    if tid in groups:
        return groups[tid].name
    return contact(tid).name


def short_title(tid, limit=20):
    """thread_title() cut to fit a header or a row."""
    return _shorten(thread_title(tid), limit)


def _avatar_key(cid):
    c = contact(cid)
    return (cid, c.avatar, c.initial(), c.tint())


def thread_avatar(tid, size):
    """Round avatar of a conversation; groups show their first two members."""
    size = int(size)
    g = groups.get(tid)
    if g is None:
        key = ("avatar",) + _avatar_key(tid)
    else:
        key = ("group", tid, g.avatar) + tuple(_avatar_key(m) for m in g.members[:2])
    return _messages_thread_avatar(tid, size, key)


@memoized
def _messages_thread_avatar(tid, size, key):
    # `key` holds the avatar data, so a changed avatar makes a new cache entry.
    g = groups.get(tid)
    if g is None:
        return avatar(tid, size)
    if g.avatar is not None:
        return store.AlphaMask(
            cover(g.avatar, size, size),
            art("common/avatar_mask", size=(size, size), fit="fill"),
        )
    if len(g.members) >= 2:
        small = int(size * 0.68)
        ring = int(size * 0.72)
        return store.Fixed(
            store.Fixed(avatar(g.members[0], small), xysize=(small, small), xalign=0.0, yalign=0.0),
            store.Fixed(art("messages/group_ring", size=(ring, ring), fit="fill"), xysize=(ring, ring), xalign=1.0, yalign=1.0),
            store.Fixed(avatar(g.members[1], small), xysize=(small, small), xalign=1.0, yalign=1.0,
                        xoffset=-(ring - small) // 2, yoffset=-(ring - small) // 2),
            xysize=(size, size),
        )
    return avatar(g.members[0] if g.members else None, size)


def sender_name(sender):
    return player_name() if sender is None else contact(sender).name


# Templates (static; built by Chat and Reply) ---------------------------------

class _Item(python_object):
    """One queued step of a Chat. Never mutated once built."""

    def __init__(self, kind, text=None, image=None, sender=None, replies=None, effects=()):
        self.kind = kind
        self.text = text
        self.image = image
        self.sender = sender
        self.replies = tuple(replies) if replies else None
        self.effects = tuple(effects)

    def with_replies(self, replies):
        return _Item(self.kind, self.text, self.image, self.sender, replies, self.effects)

    def __repr__(self):
        return "<phone chat item {} {!r}>".format(self.kind, self.text if self.image is None else self.image)


class Reply(python_object):
    """A reply the player can pick.

    `text`      what the player sends ("[var]" is interpolated).
    `then`      follow-up: a Chat (for this or another conversation; Chat()
                with no contact means "this conversation"), or a list of Chats
                and plain strings (said by the conversation's contact).
    `effects`   Ren'Py action or list of actions run when the reply is chosen.
    `image`     optional image the player sends instead of / with the text.
    """

    def __init__(self, text, then=None, effects=None, image=None):
        self.text = text
        self.image = image
        self.then = then
        self.effects = tuple(as_list(effects))
        check_picklable(self.effects, "phone.Reply effects")
        check_picklable(then, "phone.Reply then")

    def __repr__(self):
        return "<phone.Reply {!r}>".format(self.text)


class Chat(object):
    """Fluent builder for a conversation. Every method returns the Chat.

    `who` is a Contact, a Group, or an id. Use Chat() without `who` for a
    reply's follow-up in the same conversation.
    """

    def __init__(self, who=None):
        self.who = None if who is None else thread_id(who)
        self.items = []

    def __repr__(self):
        return "<phone.Chat {} ({} items)>".format(self.who, len(self.items))

    def say(self, text, sender=None):
        """An incoming message. In a group, `sender` says who wrote it."""
        return self._add(_Item(TEXT, text=text, sender=_sender_id(sender)))

    def image(self, img, sender=None):
        """An incoming picture (image name or displayable)."""
        return self._add(_Item(IMAGE, image=img, sender=_sender_id(sender)))

    def _add(self, item):
        # Groups defined later in the scripts are checked by send() instead.
        if self.who is not None and self.who in groups:
            _validate(self.who, [item])
        self.items.append(item)
        return self

    def me(self, text, image=None):
        """A message the player sends without choosing it."""
        self.items.append(_Item(ME, text=text, image=image))
        return self

    def note(self, text):
        """A centered system line, e.g. a date separator."""
        self.items.append(_Item(NOTE, text=text))
        return self

    def choice(self, *replies):
        """Offers replies on the last message, or as a standalone prompt."""
        replies = [r if isinstance(r, Reply) else Reply(r) for r in replies]
        if not replies:
            raise Exception("phone.Chat.choice() needs at least one Reply.")
        last = self.items[-1] if self.items else None
        if last is not None and last.kind in _MESSAGE_KINDS and last.replies is None:
            item = last.with_replies(replies)
        else:
            item = _Item(_PROMPT, replies=replies)
        if self.who is not None and self.who in groups:
            _validate(self.who, [item])
        if item.kind == _PROMPT:
            self.items.append(item)
        else:
            self.items[-1] = item
        return self

    def effect(self, *actions):
        """Runs Ren'Py actions when playback reaches this point."""
        check_picklable(actions, "phone.Chat.effect()")
        self.items.append(_Item(_EFFECT, effects=actions))
        return self

    def set(self, var, value):
        """Sets a store variable when playback reaches this point."""
        return self.effect(store.SetVariable(var, value))

    def add(self, var, amount=1):
        """Adds to a store variable when playback reaches this point."""
        return self.effect(store.IncrementVariable(var, amount))

    def send(self):
        """Queues a copy of this chat and delivers it (see module docs)."""
        if self.who is None:
            raise Exception("phone.Chat.send(): this Chat has no contact or group.")
        _validate(self.who, self.items)
        _enqueue(self.who, list(self.items))
        return self


def _sender_id(sender):
    return None if sender is None else contact_id(sender)


# Saved state -----------------------------------------------------------------
#
# Every saved class declares class-level defaults, and fills in missing
# containers when unpickled, so fields added in later versions load from
# older saves.

class _Saved(object):
    _containers = ()  # (field, factory) for mutable fields

    def __setstate__(self, d):
        for name, factory in self._containers:
            if name not in d:
                d[name] = factory()
        self.__dict__.update(d)


class Entry(_Saved):
    """A delivered message in a conversation log."""

    uid = 0
    kind = TEXT
    text = None
    image = None
    sender = None
    time = None

    def __init__(self, uid, kind, text=None, image=None, sender=None, time=None):
        self.uid = uid
        self.kind = kind
        self.text = text
        self.image = image
        self.sender = sender  # contact id, None for the player or a note
        self.time = time

    def __repr__(self):
        return "<phone message {} {} {!r}>".format(self.kind, self.sender, self.text if self.image is None else self.image)

    @property
    def incoming(self):
        return self.kind in (TEXT, IMAGE)


class Option(_Saved):
    """A reply offered to the player; matched by uid, never by text."""

    uid = 0
    text = None
    image = None
    reply = None

    def __init__(self, uid, text, image, reply):
        self.uid = uid
        self.text = text
        self.image = image
        self.reply = reply

    def __repr__(self):
        return "<phone reply option {} {!r}>".format(self.uid, self.text)


class Conversation(_Saved):
    _containers = (("log", list), ("pending", list))
    id = None
    unread = 0
    choice = None
    stamp = 0

    def __init__(self, tid):
        self.id = tid
        self.log = []  # delivered Entries
        self.pending = []  # _Items waiting to be delivered
        self.unread = 0
        self.choice = None  # list of Options while waiting for the player
        self.stamp = 0  # inbox order; bumped on delivery

    def next_is_incoming(self):
        for item in self.pending:
            if item.kind in (TEXT, IMAGE):
                return True
            if item.kind in (ME, NOTE, _PROMPT):
                return False
        return False


class MessagesState(_Saved):
    _containers = (("threads", dict),)
    version = 1

    def __init__(self):
        self.version = 1
        self.threads = {}  # thread id -> Conversation

    def get(self, who, create=True):
        tid = thread_id(who)
        conv = self.threads.get(tid)
        if conv is None and create:
            conv = self.threads[tid] = Conversation(tid)
        return conv

    def inbox(self):
        """Conversations with something to show, newest first."""
        rv = [c for c in self.threads.values() if c.log or c.choice]
        rv.sort(key=lambda c: -c.stamp)
        return rv

    def badge(self):
        return sum(c.unread + (1 if c.choice else 0) for c in self.threads.values())


def conversation(who):
    """The conversation with `who`, for display. Never creates saved state."""
    tid = thread_id(who)
    return messages_state.threads.get(tid) or Conversation(tid)


def _state():
    return globals().get("messages_state")


# Delivery --------------------------------------------------------------------

def viewing(who):
    """True while the phone shows this conversation."""
    if not is_showing(THREAD_SCREEN):
        return False
    return state.current()[1].get("thread") == thread_id(who)


def _typing_delay():
    return cfg.messages_typing_delay or 0


def _animated(conv):
    return _typing_delay() > 0 and viewing(conv.id)


def _validate(tid, items, seen=None):
    """Checks items for conversation `tid`, following every reply's `then`
    (loops are fine). Raises before anything is queued or shown."""
    if seen is None:
        seen = python_set()
    is_group = tid in groups
    for item in items:
        if is_group and item.kind in (TEXT, IMAGE) and item.sender is None:
            raise Exception(
                "phone: a message in group chat {!r} has no sender ({!r}). In a group use "
                ".say(text, sender=...), and in Reply(then=...) use "
                "phone.Chat().say(text, sender=...) instead of a plain string.".format(tid, item.text or item.image)
            )
        for reply in item.replies or ():
            key = (tid, id(reply))
            if key in seen:
                continue
            seen.add(key)
            for t, its in _expand_then(reply.then, tid):
                _validate(t, its, seen)


def _enqueue(tid, items):
    """Appends items to a conversation and delivers what can be delivered."""
    conv = messages_state.get(tid)
    conv.pending.extend(items)
    _dispatch(conv)


def _dispatch(conv):
    """Delivers now, unless the conversation is on screen (then the thread
    screen plays it back with a typing indicator)."""
    if _animated(conv):
        return
    delivered = _deliver_all(conv)
    incoming = [e for e in delivered if e.incoming]
    if incoming and not viewing(conv.id):
        _notify(conv, incoming[-1])


def _deliver_all(conv):
    rv = []
    while conv.pending and conv.choice is None:
        entry = _deliver_one(conv)
        if entry is not None:
            rv.append(entry)
    return rv


def _deliver_one(conv):
    """Delivers the next pending item. Returns the new log Entry, if any."""
    item = conv.pending.pop(0)
    if item.kind == _EFFECT:
        run_effects(item.effects)
        return None

    entry = None
    if item.kind != _PROMPT:
        entry = Entry(
            state.next_uid(), item.kind,
            text=_interpolate(item.text), image=item.image,
            sender=item.sender if item.kind in (TEXT, IMAGE) else None,
            time=clock_text(),
        )
        if entry.incoming and entry.sender is None:
            entry.sender = conv.id  # 1:1 conversation: the contact wrote it
        conv.log.append(entry)
        if entry.incoming:
            if not viewing(conv.id):
                conv.unread += 1
            if entry.sender in contacts and not contact(entry.sender).known:
                state.set_contact_data(entry.sender, "known", True)

    if item.replies:
        conv.choice = [
            Option(state.next_uid(), _interpolate(r.text), r.image, r) for r in item.replies
        ]

    conv.stamp = state.next_uid()
    return entry


def _interpolate(text):
    if text is None:
        return None
    return renpy.substitute(text)


def _notify(conv, entry):
    title = thread_title(conv.id)
    body = preview(entry)
    if conv.id in groups and entry.sender is not None:
        body = "{}: {}".format(sender_name(entry.sender), body)
    notify(_shorten(title, 30), _shorten(body, 36), app_id="messages")


def preview(entry):
    """Short text for a log entry (inbox rows and banners)."""
    if entry is None:
        return ""
    text = entry.text or ""
    if entry.image is not None and not text:
        text = renpy.translate_string("Photo")
    return " ".join(text.split())


def _shorten(text, limit):
    limit = max(8, int(limit / text_scale()))
    if len(text) <= limit:
        return text
    return text[:limit - 1].rstrip() + "…"


def inbox_preview(conv):
    """Last message line of an inbox row."""
    last = conv.log[-1] if conv.log else None
    if last is None:
        return renpy.translate_string("Tap to reply")
    text = preview(last)
    if last.kind == ME:
        text = renpy.translate_string("You: ") + text
    elif last.incoming and conv.id in groups:
        text = "{}: {}".format(sender_name(last.sender), text)
    return _shorten(text, 24)


def inbox_time(conv):
    for entry in reversed(conv.log):
        if entry.time:
            return entry.time
    return None


def group_members_line(tid):
    g = groups.get(tid)
    if g is None:
        return ""
    return _shorten(", ".join([contact(m).name for m in g.members] + [renpy.translate_string("You")]), 32)


def thumbnail(img, width=None, ratio=0.75):
    """Rounded, cropped preview of an image message."""
    w = int(width or content_size()[0] * 0.55)
    h = int(w * ratio)
    return _messages_thumbnail(img, w, h)


@memoized
def _messages_thumbnail(img, w, h):
    if w > px(100):
        mask = art_frame("messages/thumb_mask", 18)
    else:
        mask = art_frame("messages/thumb_mask_small", 8)
    return store.AlphaMask(cover(img, w, h), store.Fixed(mask, xysize=(w, h)))


def bubble_tail(entries, index, typing=False):
    """True if entries[index] ends a run of bubbles from one sender, so it
    is drawn with a tail. While someone is typing, the typing bubble takes
    the tail from the last incoming message."""
    entry = entries[index]
    nxt = entries[index + 1] if index + 1 < len(entries) else None
    if entry.kind == ME:
        return nxt is None or nxt.kind != ME
    if nxt is None:
        return not typing
    return not nxt.incoming or nxt.sender != entry.sender


def _tick(tid):
    """Plays back the next visible message of a conversation on screen."""
    conv = messages_state.get(tid)
    while conv.pending and conv.choice is None:
        entry = _deliver_one(conv)
        if entry is not None:
            if entry.incoming:
                play_sound("message")
            return entry
    return None


def _flush_idle():
    """Delivers messages left pending by a conversation the player stopped
    watching mid-playback. Runs at the start of every interaction."""
    s = _state()
    if s is None or globals().get("state") is None:
        return
    for conv in list(s.threads.values()):
        if conv.pending and conv.choice is None and not viewing(conv.id):
            _dispatch(conv)


if _flush_idle not in store.config.interact_callbacks:
    store.config.interact_callbacks.append(_flush_idle)


def _expand_then(then, tid):
    """Turns a Reply's `then` into [(thread id, [items])]."""
    rv = []
    for part in as_list(then):
        if isinstance(part, Chat):
            rv.append((part.who or tid, list(part.items)))
        elif isinstance(part, str):
            rv.append((tid, [_Item(TEXT, text=part)]))
        elif isinstance(part, _Item):
            rv.append((tid, [part]))
        else:
            raise Exception("phone.Reply then= must be a Chat, a string or a list of them, not {!r}.".format(part))
    return rv


def choose(who, uid):
    """Answers the pending choice of a conversation with the option `uid`.

    Returns False if that option is not on offer (e.g. a stale button).
    """
    conv = messages_state.get(who)
    option = None
    for o in conv.choice or ():
        if o.uid == uid:
            option = o
            break
    if option is None:
        return False

    # Validate before changing anything, so a bad follow-up can't leave the
    # conversation half answered.
    follow_ups = _expand_then(option.reply.then, conv.id)
    for tid, items in follow_ups:
        _validate(tid, items)

    conv.choice = None
    conv.log.append(Entry(state.next_uid(), ME, text=option.text, image=option.image, time=clock_text()))
    conv.stamp = state.next_uid()

    front = []
    touched = [conv]
    for tid, items in follow_ups:
        if tid == conv.id:
            front.extend(items)
        else:
            other = messages_state.get(tid)
            other.pending.extend(items)
            if other not in touched:
                touched.append(other)
    conv.pending[:0] = front

    # The follow-ups are queued before the effects run: a Jump or Call effect
    # raises, and delivery still happens on the way out.
    try:
        run_effects(option.reply.effects)
    finally:
        for c in touched:
            _dispatch(c)
    return True


def mark_read(who):
    conv = messages_state.get(who, create=False)
    if conv is not None:
        conv.unread = 0


# Public API --------------------------------------------------------------------

def text(who, message, *replies, sender=None):
    """Sends one message, optionally offering replies: phone.text(eileen, "Hi!", phone.Reply("Hey")).
    In a group, `sender` says who wrote it."""
    chat = Chat(who).say(message, sender=sender)
    if replies:
        chat.choice(*replies)
    chat.send()


def send_image(who, img, sender=None):
    """Sends a picture from `who` (or from `sender` in a group)."""
    Chat(who).image(img, sender=sender).send()


def open_chat(who):
    """Opens the phone on a conversation and waits until the player closes it."""
    tid = thread_id(who)
    messages_state.get(tid)
    mark_read(tid)
    if renpy.get_screen("phone_notification", layer=cfg.layer):
        renpy.hide_screen("phone_notification", layer=cfg.layer)
    open("messages", THREAD_SCREEN, thread=tid)


def waiting_for_reply(who):
    """True while the conversation waits for the player to pick a reply."""
    _flush_idle()
    conv = messages_state.get(who, create=False)
    return bool(conv is not None and conv.choice)


def unread(who=None):
    """Unread messages in one conversation, or in all of them."""
    if who is None:
        return sum(c.unread for c in messages_state.threads.values())
    conv = messages_state.get(who, create=False)
    return conv.unread if conv is not None else 0


def clear_chat(who):
    """Deletes a conversation: log, queued messages and pending choice."""
    messages_state.threads.pop(thread_id(who), None)


def chat_log(who):
    """The delivered entries of a conversation (Entry objects: kind, text,
    image, sender, time)."""
    conv = messages_state.get(who, create=False)
    return list(conv.log) if conv is not None else []


def reply_options(who):
    """The replies currently offered in a conversation (Option objects)."""
    conv = messages_state.get(who, create=False)
    return list(conv.choice or ()) if conv is not None else []


def choose_reply(who, index):
    """Picks the reply at `index` from script, as if the player tapped it."""
    options = reply_options(who)
    if not 0 <= index < len(options):
        raise Exception("phone.choose_reply: {!r} has no reply number {}.".format(thread_id(who), index))
    return choose(who, options[index].uid)


# Screen actions ----------------------------------------------------------------

def _scroll_to_end(adj):
    if adj is not None:
        adj.value = float("inf")  # Adjustment clamps this to the bottom


class MessagesOpen(PhoneAction):
    """Opens a conversation from the inbox and marks it read."""

    def __init__(self, thread):
        self.thread = thread

    def run(self):
        mark_read(self.thread)
        state.navigate(THREAD_SCREEN, thread=self.thread)


class MessagesTick(PhoneAction):
    """Timer action of the conversation screen: next message arrives."""

    def __init__(self, thread, adjustment=None):
        self.thread = thread
        self.adjustment = adjustment

    def run(self):
        _tick(self.thread)
        mark_read(self.thread)
        _scroll_to_end(self.adjustment)


class MessagesChoose(PhoneAction):
    """Sends the reply option with `uid`."""

    def __init__(self, thread, uid, adjustment=None):
        self.thread = thread
        self.uid = uid
        self.adjustment = adjustment

    def run(self):
        play_sound("tap")
        choose(self.thread, self.uid)
        _scroll_to_end(self.adjustment)


def _messages_lint():
    for gid, g in groups.items():
        if gid in contacts:
            print("phone: group id {!r} is also a contact id.".format(gid))
        for m in g.members:
            if m not in contacts:
                print("phone: group {!r} has member {!r}, which is not a defined contact.".format(gid, m))


if _messages_lint not in store.config.lint_hooks:
    store.config.lint_hooks.append(_messages_lint)


def _messages_after_load():
    """Brings older saves of the Messages state up to date."""
    s = _state()
    if s is None:
        return
    for k, v in MessagesState().__dict__.items():
        if not hasattr(s, k):
            setattr(s, k, v)


if _messages_after_load not in store.config.after_load_callbacks:
    store.config.after_load_callbacks.append(_messages_after_load)


"""renpy
default phone.messages_state = phone.MessagesState()
"""
