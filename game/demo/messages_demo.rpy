## Messages demo: Eileen texts the player, then a group chat with Lucy and Max.

default demo_dinner = None
default demo_messages_snacks = 0
default demo_messages_nickname = "stranger"

define demo_crew = phone.group("demo_crew", "Weekend crew", [lucy, max_])

# Chats are templates: define them once, send them whenever the story needs.
define demo_eileen_dinner = phone.Chat(eileen).note(_("Today")).say(_("Hey [demo_messages_nickname]! Are you free tonight?")).choice(
    phone.Reply(
        _("Sure, what's up?"),
        then=phone.Chat().say(_("A new ramen place opened downtown.")).say(_("8pm?")).choice(
            phone.Reply(_("Count me in!"), effects=SetVariable("demo_dinner", True), then=[_("Yay! See you there.")]),
            phone.Reply(_("Maybe next time."), effects=SetVariable("demo_dinner", False), then=[_("No worries!")]),
        ),
    ),
    phone.Reply(_("Busy tonight, sorry."), then=phone.Chat().say(_("Ah, okay. Another time!")).set("demo_dinner", False)),
)

define demo_crew_photos = phone.Chat(demo_crew).say(_("Look where I am!"), sender=lucy).image("demo photo beach", sender=lucy).say(
    _("Unfair. I'm stuck at work."), sender=max_
).image("demo photo city", sender=max_).say(_("Should we all go next weekend?"), sender=lucy).choice(
    phone.Reply(_("Yes! I'll bring snacks."), then=phone.Chat().say(_("Best. Friend. Ever."), sender=max_).add("demo_messages_snacks", 1)),
    phone.Reply(_("Only if there's a cat."), then=phone.Chat().image("demo photo cat", sender=lucy).say(_("Deal."), sender=lucy)),
)


label demo_messages:
    "My phone buzzes. A message from Eileen."
    $ demo_eileen_dinner.send()
    $ phone.open_chat(eileen)

    while phone.waiting_for_reply(eileen):
        "I should answer Eileen."
        $ phone.open_chat(eileen)

    if demo_dinner:
        e "Ramen at eight, then!"
    else:
        e "Maybe next week."

    "Then the group chat lights up."
    $ demo_crew_photos.send()
    $ phone.open("messages")

    if demo_messages_snacks:
        "I'm on snack duty now."
    "That's the Messages app."
    return
