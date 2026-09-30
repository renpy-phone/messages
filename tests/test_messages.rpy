## Tests for the Messages app: model, regressions of the old prototype,
## playback, screens and saving.

define _tmsg_ann = phone.Contact("_tmsg_ann", "Ann Lee")
define _tmsg_bob = phone.Contact("_tmsg_bob", "Bob Stone")
define _tmsg_cat = phone.Contact("_tmsg_cat", "Cat Diaz")
define _tmsg_crew = phone.group("_tmsg_crew", "Study group", [_tmsg_bob, _tmsg_cat])

default _tmsg_flag = None
default _tmsg_count = 0
default _tmsg_name = "Robin"

# Built at init time: must not touch saved state (regression 3).
define _tmsg_branch = phone.Chat().say("Branch message").set("_tmsg_flag", "branch")
define _tmsg_hello = phone.Chat(_tmsg_ann).say("Hello").say("How are you?").choice(
    phone.Reply("Good", then=_tmsg_branch),
    phone.Reply("Great", then=_tmsg_branch),
).say("Bye")

init python:
    def _tmsg_texts(who):
        return [e.text for e in phone.chat_log(who)]

    def _tmsg_kinds(who):
        return [e.kind for e in phone.chat_log(who)]

    def _tmsg_uids(who):
        return [o.uid for o in phone.reply_options(who)]

screen _tmsg_closer(delay=0.5):
    timer delay action [Hide("_tmsg_closer"), phone.Close()]


label test_messages_delivery:
    python:
        chat = phone.Chat("_tmsg_ann").say("One").say("Two", sender=None).choice(phone.Reply("Yes", then=["Front"])).say("Three")
        phone.Chat("_tmsg_ann").say("Four").send()  # nothing waits yet: delivered
        chat.send()
        expect_eq(_tmsg_texts("_tmsg_ann"), ["Four", "One", "Two"], "delivered up to and including the first choice")
        expect(phone.waiting_for_reply("_tmsg_ann"), "waits for a reply")
        expect_eq(phone.unread("_tmsg_ann"), 3, "unread counts incoming messages")
        expect_eq(phone.get_app("messages").badge(), 4, "badge = unread + waiting conversations")
        expect_eq([o.text for o in phone.reply_options("_tmsg_ann")], ["Yes"], "reply options")

        phone.Chat("_tmsg_ann").say("Queued behind the choice").send()
        expect_eq(len(phone.chat_log("_tmsg_ann")), 3, "later sends wait behind the choice")

        expect(phone.choose_reply("_tmsg_ann", 0), "choose_reply works")
        expect_eq(_tmsg_texts("_tmsg_ann"), ["Four", "One", "Two", "Yes", "Front", "Three", "Queued behind the choice"],
                  "reply, then its follow-up in front of the rest of the queue")
        expect_eq(_tmsg_kinds("_tmsg_ann")[3], "me", "the reply is the player's message")
        expect(not phone.waiting_for_reply("_tmsg_ann"), "no longer waiting")
        expect_eq(phone.chat_log("_tmsg_ann")[0].sender, "_tmsg_ann", "1:1 messages come from the contact")
        expect(phone.contact("_tmsg_ann").known, "texting makes a contact known")

        phone.mark_read("_tmsg_ann")
        expect_eq(phone.unread(), 0, "mark_read")

        phone.text("_tmsg_bob", "Plain text")
        phone.send_image("_tmsg_bob", "demo photo cat")
        log = phone.chat_log("_tmsg_bob")
        expect_eq([e.kind for e in log], ["text", "image"], "text() and send_image() shortcuts")
        expect_eq(log[1].image, "demo photo cat", "image payload")

        phone.Chat("_tmsg_bob").note("Yesterday").me("I sent this").send()
        expect_eq(_tmsg_kinds("_tmsg_bob")[2:], ["note", "me"], "notes and player messages")
        expect_eq(phone.unread("_tmsg_bob"), 2, "notes and player messages are not unread")

        # A choice on an empty chat is a standalone prompt.
        phone.Chat("_tmsg_cat").choice(phone.Reply("Hi Cat")).send()
        expect_eq(phone.chat_log("_tmsg_cat"), [], "a prompt adds no message")
        expect(phone.waiting_for_reply("_tmsg_cat"), "a prompt waits for a reply")
        expect_eq(phone.messages_state.inbox()[0].id, "_tmsg_cat", "a prompt shows in the inbox")
        expect(not phone.choose("_tmsg_cat", -1), "unknown uids are ignored")
        phone.choose_reply("_tmsg_cat", 0)
        expect_eq(_tmsg_texts("_tmsg_cat"), ["Hi Cat"], "answering a prompt")

        phone.clear_chat("_tmsg_cat")
        expect_eq(phone.chat_log("_tmsg_cat"), [], "clear_chat")
        expect("_tmsg_cat" not in phone.messages_state.threads, "clear_chat removes the conversation")
    return


label test_messages_regression_same_text:
    # Regression 1: replies were matched by text.
    python:
        phone.Chat("_tmsg_ann").say("Pick one").choice(
            phone.Reply("OK", then=["First branch"]),
            phone.Reply("OK", then=["Second branch"]),
        ).send()
        uids = _tmsg_uids("_tmsg_ann")
        expect_eq(len(set(uids)), 2, "options with the same text get different uids")
        phone.choose("_tmsg_ann", uids[1])
        expect_eq(_tmsg_texts("_tmsg_ann")[-1], "Second branch", "the second same-text option leads to its own branch")

        ok = phone.Reply("OK")
        phone.Chat("_tmsg_ann").say("Question 1").choice(ok).say("Question 2").choice(ok).send()
        first = _tmsg_uids("_tmsg_ann")
        phone.choose("_tmsg_ann", first[0])
        expect(phone.waiting_for_reply("_tmsg_ann"), "second OK prompt offered")
        expect(not phone.choose("_tmsg_ann", first[0]), "a used option cannot be chosen again")
        phone.choose_reply("_tmsg_ann", 0)
        expect_eq(_tmsg_texts("_tmsg_ann")[-4:], ["Question 1", "OK", "Question 2", "OK"], "the same reply works twice")
        expect(not phone.waiting_for_reply("_tmsg_ann"), "both answered")
    return


label test_messages_regression_choice_target:
    # Regression 2: add_replies checked the first pending message but wrote the last.
    python:
        chat = phone.Chat("_tmsg_ann").say("A").choice(phone.Reply("to A")).say("B").choice(phone.Reply("to B"))
        expect_eq([i.kind for i in chat.items], ["text", "text"], "choices attach to their own message")
        expect_eq([i.replies[0].text for i in chat.items], ["to A", "to B"], "each message keeps its replies")

        chat2 = phone.Chat("_tmsg_ann").say("C").choice(phone.Reply("1")).choice(phone.Reply("2"))
        expect_eq([i.kind for i in chat2.items], ["text", "prompt"], "a second choice becomes a prompt")
        expect_eq(chat2.items[0].replies[0].text, "1", "the first choice is not overwritten")

        chat.send()
        expect_eq([o.text for o in phone.reply_options("_tmsg_ann")], ["to A"], "first choice offered first")
        phone.choose_reply("_tmsg_ann", 0)
        expect_eq([o.text for o in phone.reply_options("_tmsg_ann")], ["to B"], "then the second")
    return


label test_messages_regression_reusable_builder:
    # Regression 3: send() consumed the builder's queue.
    python:
        expect_eq(phone.messages_state.threads, {}, "defining chats at init creates no conversations")
        expect_eq(len(_tmsg_hello.items), 3, "defined chat keeps its items")

        _tmsg_flag = None
        _tmsg_hello.send()
        phone.choose_reply("_tmsg_ann", 0)
        expect_eq(_tmsg_texts("_tmsg_ann"), ["Hello", "How are you?", "Good", "Branch message", "Bye"], "first send")
        expect_eq(_tmsg_flag, "branch", "branch effect ran")

        _tmsg_flag = None
        _tmsg_hello.send()
        expect_eq(len(_tmsg_hello.items), 3, "send() leaves the builder intact")
        phone.choose_reply("_tmsg_ann", 1)
        expect_eq(_tmsg_texts("_tmsg_ann")[5:], ["Hello", "How are you?", "Great", "Branch message", "Bye"],
                  "a chat and a shared branch can be sent again")
        expect_eq(_tmsg_flag, "branch", "shared branch effect ran again")
    return


label test_messages_regression_order_on_delivery:
    # Regression 4: the conversation moved to the top when the chat was built.
    python:
        phone.text("_tmsg_ann", "Ann first")
        phone.text("_tmsg_bob", "Bob second")
        later = phone.Chat("_tmsg_ann").say("Built now, sent later")
        expect_eq([c.id for c in phone.messages_state.inbox()], ["_tmsg_bob", "_tmsg_ann"], "building does not reorder")
        later.send()
        expect_eq([c.id for c in phone.messages_state.inbox()], ["_tmsg_ann", "_tmsg_bob"], "delivery moves to the top")

        # Queued behind a choice: moves only once it is delivered.
        phone.Chat("_tmsg_bob").say("Choose").choice(phone.Reply("Done")).send()
        phone.text("_tmsg_ann", "Ann again")
        phone.text("_tmsg_bob", "Waiting in Bob's queue")
        expect_eq(phone.messages_state.inbox()[0].id, "_tmsg_ann", "a queued message does not reorder")
        phone.choose_reply("_tmsg_bob", 0)
        expect_eq(phone.messages_state.inbox()[0].id, "_tmsg_bob", "it reorders on delivery")
    return


label test_messages_regression_cross_thread:
    # Regression 5: a follow-up for another conversation left the first stuck.
    python:
        phone.Chat("_tmsg_ann").say("Ask Bob?").choice(
            phone.Reply("Sure", then=phone.Chat("_tmsg_bob").say("Ann says hi")),
        ).say("Thanks!").send()
        phone.choose_reply("_tmsg_ann", 0)
        expect_eq(_tmsg_texts("_tmsg_ann"), ["Ask Bob?", "Sure", "Thanks!"], "the first conversation carries on")
        expect_eq(_tmsg_texts("_tmsg_bob"), ["Ann says hi"], "the follow-up reaches the other conversation")
        expect_eq(phone.unread("_tmsg_bob"), 1, "and counts as unread there")

        # A mixed follow-up: some for this conversation, some for another.
        phone.Chat("_tmsg_ann").say("Group?").choice(
            phone.Reply("Yes", then=[phone.Chat("_tmsg_crew").say("Welcome!", sender=_tmsg_cat), "Added you"]),
        ).send()
        phone.choose_reply("_tmsg_ann", 0)
        expect_eq(_tmsg_texts("_tmsg_ann")[-1], "Added you", "strings in then= stay in this conversation")
        expect_eq(_tmsg_texts("_tmsg_crew"), ["Welcome!"], "chats in then= go to their conversation")
    return


label test_messages_regression_effects_at_playback:
    # Regression 6: effects ran when the chat was sent.
    python:
        _tmsg_flag = None
        _tmsg_count = 0
        phone.Chat("_tmsg_ann").say("Before").choice(
            phone.Reply("Answer", effects=[SetVariable("_tmsg_flag", "reply")], then=phone.Chat().add("_tmsg_count", 5)),
        ).set("_tmsg_flag", "after").add("_tmsg_count").send()
        expect_eq(_tmsg_flag, None, "effects behind a choice have not run")
        expect_eq(_tmsg_count, 0, "add() behind a choice has not run")
        phone.choose_reply("_tmsg_ann", 0)
        expect_eq(_tmsg_flag, "after", "reply effect then queued effect ran, in order")
        expect_eq(_tmsg_count, 6, "follow-up add() and queued add() ran")

        # Effects in a playing-back conversation wait for playback.
        _tmsg_flag = None
        phone.cfg.messages_typing_delay = 0.3
        phone.show("messages", "phone_messages_thread", thread="_tmsg_ann")
        phone.Chat("_tmsg_ann").say("Typing...").set("_tmsg_flag", "played").send()
        expect_eq(_tmsg_flag, None, "effect waits while the conversation plays back")
    $ wait(1.2)
    $ expect_eq(_tmsg_flag, "played", "effect ran when playback reached it")
    $ phone.close()
    $ phone.cfg.messages_typing_delay = 0.8
    return


label test_messages_interpolation:
    python:
        _tmsg_name = "Robin"
        chat = phone.Chat("_tmsg_ann").say("Hi [_tmsg_name]!").choice(phone.Reply("I'm [_tmsg_name]"))
        _tmsg_name = "Sam"
        chat.send()
        _tmsg_name = "Alex"
        phone.choose_reply("_tmsg_ann", 0)
        expect_eq(_tmsg_texts("_tmsg_ann"), ["Hi Sam!", "I'm Sam"], "text is interpolated when it is sent")
    return


label test_messages_group:
    python:
        try:
            phone.Chat(_tmsg_crew).say("No sender").send()
            expect(False, "group messages without a sender are refused")
        except Exception:
            pass
        phone.Chat(_tmsg_crew).note("Today").say("Hey all", sender=_tmsg_bob).say("Hi!", sender="_tmsg_cat").image("demo photo beach", sender=_tmsg_cat).send()
        log = phone.chat_log("_tmsg_crew")
        expect_eq([e.sender for e in log], [None, "_tmsg_bob", "_tmsg_cat", "_tmsg_cat"], "per-message senders")
        expect_eq(phone.unread(_tmsg_crew), 3, "group unread")
        expect_eq(phone.thread_title("_tmsg_crew"), "Study group", "group title")
        expect(phone.is_group("_tmsg_crew"), "is_group")
        expect_eq(phone.inbox_preview(phone.conversation("_tmsg_crew")), "Cat Diaz: Photo", "group preview names the sender")
    return


label test_messages_notification:
    python:
        renpy.hide_screen("phone_notification", layer=phone.cfg.layer)
        phone.text("_tmsg_ann", "Are you there?")
        expect(renpy.get_screen("phone_notification", layer=phone.cfg.layer) is not None, "a banner appears while the phone is closed")
    $ shot("messages-banner")
    python:
        renpy.hide_screen("phone_notification", layer=phone.cfg.layer)
        phone.show("messages")
        phone.text("_tmsg_bob", "Phone is open")
        expect(renpy.get_screen("phone_notification", layer=phone.cfg.layer) is None, "no banner while the phone is open")
        expect_eq(phone.unread("_tmsg_bob"), 1, "unread while on the inbox")
    $ phone.close()
    return


label test_messages_playback:
    # Checks sit mid-way between deliveries so slow renders don't race them.
    $ phone.cfg.messages_typing_delay = 1.0
    $ phone.Chat("_tmsg_ann").say("Earlier message").send()
    $ phone.show("messages")
    $ phone.MessagesOpen("_tmsg_ann")()
    $ expect_eq(phone.unread("_tmsg_ann"), 0, "opening a conversation marks it read")
    $ phone.Chat("_tmsg_ann").say("One").say("Two").choice(
        phone.Reply("Reply", then=phone.Chat().say("Follow-up 1").say("Follow-up 2"))).send()
    $ expect_eq(len(phone.chat_log("_tmsg_ann")), 1, "nothing arrives instantly while watching")
    $ expect(phone.conversation("_tmsg_ann").next_is_incoming(), "typing indicator is shown")
    $ wait(1.4)
    $ expect_eq(len(phone.chat_log("_tmsg_ann")), 2, "messages arrive one at a time")
    $ wait(1.2)
    $ expect_eq(_tmsg_texts("_tmsg_ann"), ["Earlier message", "One", "Two"], "playback stops at the choice")
    $ expect_eq(phone.unread("_tmsg_ann"), 0, "messages seen on screen are not unread")
    $ phone.MessagesChoose("_tmsg_ann", _tmsg_uids("_tmsg_ann")[0])()
    $ expect_eq(_tmsg_texts("_tmsg_ann")[-1], "Reply", "the reply appears at once")
    $ expect_eq(len(phone.conversation("_tmsg_ann").pending), 2, "follow-ups play back with typing")
    $ wait(1.4)
    $ expect_eq(_tmsg_texts("_tmsg_ann")[-1], "Follow-up 1", "first follow-up")
    # Leaving mid-playback delivers the rest.
    $ phone.Back()()
    $ wait(0.2)
    $ expect_eq(_tmsg_texts("_tmsg_ann")[-1], "Follow-up 2", "leaving delivers what was still queued")
    $ expect_eq(phone.unread("_tmsg_ann"), 1, "and it is unread")

    # 0 delay: instant even on screen.
    $ phone.cfg.messages_typing_delay = 0
    $ phone.MessagesOpen("_tmsg_ann")()
    $ phone.text("_tmsg_ann", "Instant")
    $ expect_eq(_tmsg_texts("_tmsg_ann")[-1], "Instant", "delay 0 delivers at once")
    $ phone.close()
    $ phone.cfg.messages_typing_delay = 0.8
    return


label test_messages_open_chat:
    $ phone.text("_tmsg_ann", "Open me", phone.Reply("Opened"))
    $ expect_eq(phone.unread("_tmsg_ann"), 1, "unread before opening")
    show screen _tmsg_closer(0.5)
    $ phone.open_chat("_tmsg_ann")
    $ expect(not phone.is_open(), "open_chat blocks until the phone is closed")
    $ expect_eq(phone.unread("_tmsg_ann"), 0, "open_chat marks read")
    $ expect_eq(phone.state.current(), ("phone_messages_thread", {"thread": "_tmsg_ann"}), "open_chat shows the conversation")
    return


label test_messages_pickle:
    python:
        from renpy.compat.pickle import dumps, loads
        phone.Chat(_tmsg_crew).say("Hi", sender=_tmsg_bob).image("demo photo city", sender=_tmsg_cat).choice(
            phone.Reply("Nice", effects=SetVariable("_tmsg_flag", 1), then=phone.Chat().say("Thanks", sender=_tmsg_cat)),
            phone.Reply("Photo", image="demo photo beach"),
        ).set("_tmsg_flag", 2).send()
        s = loads(dumps(phone.messages_state))
        conv = s.threads["_tmsg_crew"]
        expect_eq([e.text for e in conv.log], ["Hi", None], "log survives pickling")
        expect_eq([o.uid for o in conv.choice], _tmsg_uids("_tmsg_crew"), "options keep their uids")
        expect_eq(len(conv.pending), 1, "queued effects survive pickling")
        expect(loads(dumps(_tmsg_crew)) is _tmsg_crew, "groups pickle by id")

        # Keep playing with the restored state.
        phone.messages_state = s
        _tmsg_flag = None
        phone.choose_reply("_tmsg_crew", 0)
        expect_eq(_tmsg_texts("_tmsg_crew")[-1], "Thanks", "restored follow-up plays")
        expect_eq(_tmsg_flag, 2, "restored effects run")
    return


label test_messages_screens:
    python:
        phone.Chat("_tmsg_bob").say("See you at the library at 5?").choice(phone.Reply("Sure")).send()
        phone.choose_reply("_tmsg_bob", 0)
        phone.Chat(_tmsg_crew).note("Yesterday").say("Did anyone start the essay?", sender=_tmsg_bob).say(
            "Not yet. Here's the reading list, it's long but the first two chapters are the important ones.", sender=_tmsg_cat
        ).image("demo photo city", sender=_tmsg_cat).note("Today").me("I'll bring snacks").say("Legend", sender=_tmsg_bob).send()
        phone.Chat(_tmsg_ann).note("Today").say("Hey! Long time no see").say("Are you coming to the party on Saturday? Everyone will be there and it would be great to catch up.").choice(
            phone.Reply("Of course, I'll be there!"),
            phone.Reply("I can't, sorry."),
            phone.Reply("Send a pic", image="demo photo beach"),
        ).send()
    $ renpy.hide_screen("phone_notification", layer=phone.cfg.layer)
    $ phone.show("messages")
    $ shot("messages-inbox")
    $ phone.MessagesOpen("_tmsg_ann")()
    $ shot("messages-thread-choice")
    $ phone.MessagesOpen("_tmsg_crew")()
    $ shot("messages-group")
    $ phone.Navigate("phone_image_viewer", image="demo photo city")()
    $ shot("messages-image-viewer")

    # Typing indicator: a long delay keeps it on screen.
    $ phone.cfg.messages_typing_delay = 30
    $ phone.Back()()
    $ phone.MessagesOpen("_tmsg_bob")()
    $ phone.text("_tmsg_bob", "On my way")
    $ shot("messages-typing")

    $ phone.set_theme("dark")
    $ phone.state.home()
    $ phone.Launch("messages")()
    $ shot("messages-inbox-dark")
    $ phone.MessagesOpen("_tmsg_ann")()
    $ shot("messages-thread-dark")
    $ phone.Back()()
    $ phone.MessagesOpen("_tmsg_crew")()
    $ shot("messages-group-dark")
    $ phone.Back()()
    $ phone.MessagesOpen("_tmsg_bob")()
    $ phone.text("_tmsg_bob", "Almost there")
    $ shot("messages-typing-dark")
    $ phone.set_theme("light")
    $ phone.cfg.messages_typing_delay = 0.8

    $ phone.close()
    $ phone.reset_apps()
    $ phone.show("messages")
    $ shot("messages-empty")
    $ phone.close()
    return


label test_messages_many:
    # Long logs render only the last entries.
    python:
        chat = phone.Chat("_tmsg_ann")
        for i in range(150):
            chat.say("Message {}".format(i))
        chat.send()
        expect_eq(len(phone.chat_log("_tmsg_ann")), 150, "all messages are kept")
    $ renpy.hide_screen("phone_notification", layer=phone.cfg.layer)
    $ phone.show("messages", "phone_messages_thread", thread="_tmsg_ann")
    $ shot("messages-long")
    $ phone.close()
    return


label test_messages_demo_chats:
    # The demo's chats play through.
    python:
        demo_dinner = None
        demo_eileen_dinner.send()
        expect_eq(phone.chat_log(eileen)[0].kind, "note", "demo starts with a date note")
        expect_eq(phone.chat_log(eileen)[1].text, "Hey {}! Are you free tonight?".format(phone.cfg.player_name), "player name interpolated")
        phone.choose_reply(eileen, 0)
        phone.choose_reply(eileen, 0)
        expect(demo_dinner is True, "the dinner reply sets a variable")
        expect(not phone.waiting_for_reply(eileen), "Eileen's chat is finished")

        demo_messages_snacks = 0
        demo_crew_photos.send()
        expect_eq([e.kind for e in phone.chat_log(demo_crew)], ["text", "image", "text", "image", "text"], "group chat with pictures")
        phone.choose_reply(demo_crew, 0)
        expect_eq(demo_messages_snacks, 1, "group reply effect")
        expect(phone.contact("lucy").known, "group members become known")
    return


label test_messages_jump_effect:
    # A Jump effect on a reply must not lose the reply's follow-up.
    $ _tmsg_flag = None
    $ phone.Chat("_tmsg_ann").say("Ready?").choice(
        phone.Reply("Go", effects=Jump("_tmsg_jump_target"), then=["After the jump"])).say("And after that").send()
    $ phone.choose_reply("_tmsg_ann", 0)
    $ expect(False, "the Jump effect jumps")
    return

label _tmsg_jump_target:
    $ expect_eq(_tmsg_texts("_tmsg_ann"), ["Ready?", "Go", "After the jump", "And after that"], "follow-up delivered despite the Jump")
    $ expect(not phone.waiting_for_reply("_tmsg_ann"), "nothing left waiting")
    $ expect_eq(phone.conversation("_tmsg_ann").pending, [], "nothing left queued")
    return


label test_messages_group_validation:
    python:
        def raises(fn):
            try:
                fn()
            except Exception as e:
                return "sender" in str(e)
            return False

        expect(raises(lambda: phone.Chat(_tmsg_crew).say("No sender")), "say() in a group without a sender fails at build time")
        expect(raises(lambda: phone.Chat(_tmsg_crew).say("Q", sender=_tmsg_bob).choice(phone.Reply("A", then=["plain string"]))),
               "plain strings in a group reply fail at build time")
        expect(raises(lambda: phone.Chat(_tmsg_crew).say("Q", sender=_tmsg_bob).choice(
            phone.Reply("A", then=phone.Chat().say("Ok").choice(phone.Reply("B", then=["deep"]))))),
               "nested follow-ups are checked too")
        # Chat() has no conversation yet, so send() is where it gets checked.
        loose = phone.Chat().say("Q", sender=_tmsg_bob).choice(phone.Reply("A", then=["plain string"]))
        loose.who = "_tmsg_crew"
        expect(raises(loose.send), "send() checks the whole tree")
        expect_eq(phone.chat_log("_tmsg_crew"), [], "nothing was sent")

        # Loops through a reply's then= are fine.
        loop = phone.Chat(_tmsg_crew)
        loop.say("Again?", sender=_tmsg_bob).choice(phone.Reply("Yes", then=loop), phone.Reply("No"))
        loop.send()
        phone.choose_reply(_tmsg_crew, 0)
        expect_eq([e.text for e in phone.chat_log(_tmsg_crew)], ["Again?", "Yes", "Again?"], "a looping chat works")

        # choose() validates before changing anything (bypassing the send check).
        bad = phone.Chat().say("Pick", sender=_tmsg_cat).choice(phone.Reply("Bad", then=["no sender"]))
        phone.clear_chat(_tmsg_crew)
        phone._enqueue("_tmsg_crew", list(bad.items))
        expect(raises(lambda: phone.choose_reply(_tmsg_crew, 0)), "choose() refuses a follow-up without a sender")
        expect_eq([e.text for e in phone.chat_log(_tmsg_crew)], ["Pick"], "the log is untouched")
        expect(phone.waiting_for_reply(_tmsg_crew), "the choice is still offered")

        phone.text(_tmsg_crew, "Hello group", sender=_tmsg_cat)
        phone.text(_tmsg_crew, "Quiz", phone.Reply("A"), sender=_tmsg_bob)
        expect(raises(lambda: phone.text(_tmsg_crew, "Nobody")), "text() to a group needs a sender")
    return


label test_messages_save_compat:
    python:
        from renpy.compat.pickle import dumps, loads
        expect(phone._after_load in config.after_load_callbacks, "the core after-load hook is registered")
        expect(phone._messages_after_load in config.after_load_callbacks, "the messages after-load hook is registered")
        expect(phone._after_load is not phone._messages_after_load, "hooks do not shadow each other")

        # Objects saved before a field existed load with its default.
        conv = phone.Conversation("_tmsg_ann")
        conv.log.append(phone.Entry(1, "text", text="Old"))
        del conv.__dict__["pending"]
        del conv.__dict__["stamp"]
        del conv.log[0].__dict__["time"]
        old = loads(dumps(conv))
        expect_eq(old.pending, [], "missing lists are recreated")
        expect_eq(old.stamp, 0, "missing values use class defaults")
        expect_eq(old.log[0].time, None, "entries too")
        old.pending.append("x")
        expect_eq(phone.Conversation("_tmsg_bob").pending, [], "containers are not shared")

        state = phone.MessagesState()
        del state.__dict__["threads"]
        expect_eq(loads(dumps(state)).threads, {}, "state threads recreated")
    return


label test_messages_display_cache:
    python:
        a = phone.thumbnail("demo photo cat")
        expect(a is phone.thumbnail("demo photo cat"), "thumbnails are reused across renders")
        expect(a is not phone.thumbnail("demo photo beach"), "per image")
        expect(phone.thread_avatar("_tmsg_crew", 40) is phone.thread_avatar("_tmsg_crew", 40), "group avatars are reused")
        b = phone.thread_avatar("_tmsg_ann", 40)
        phone.set_avatar("_tmsg_ann", "demo photo cat")
        expect(phone.thread_avatar("_tmsg_ann", 40) is not b, "an avatar change is picked up")
        expect_eq(phone._memo(([1],), lambda: 5), 5, "unhashable keys are built without caching")
        phone.set_theme("dark")
        expect(phone.thumbnail("demo photo cat") is not a, "a theme change rebuilds")
        phone.set_theme("light")
    return
