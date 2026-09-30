## Phone app demo: an incoming call, a missed call, and calling someone back.

label demo_calls:
    $ phone.set_time("17:52")
    "You step out of the shower just as the ringing stops."
    $ phone.missed_call("lucy")
    # Calling Lucy back from the phone runs this label.
    $ phone.set_call_label("lucy", "demo_calls_lucy")

    $ phone.set_time("18:20")
    "It's a quiet evening when your phone starts to ring again."

    # The phone rings until the player answers or declines. The call is the
    # label; the story continues on the next line when it returns.
    $ phone.incoming_call("eileen", label="demo_calls_eileen", decline_label="demo_calls_eileen_declined")

    "You put the kettle on."
    $ phone.set_time("18:34")
    "By the time you're back, you've missed a call from Max."
    $ phone.missed_call("max")

    "Lucy is probably still waiting too. Open Recents and tap her name to call her back."
    $ phone.open("calls")

    "Max can wait until tomorrow."
    $ phone.set_time(None)
    return


label demo_calls_eileen:
    e "Hey! Are you still coming to the gallery opening on Saturday?"
    e "Lucy says she's bringing the whole art club."
    e "Great. See you there!"
    return


label demo_calls_eileen_declined:
    "You let it go to voicemail. Eileen will understand."
    return


label demo_calls_lucy:
    l "Oh, hi! I tried you earlier."
    l "Eileen told you about Saturday? I'll save you a spot."
    return
