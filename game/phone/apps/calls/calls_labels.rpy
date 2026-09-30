## Runs a call label as a story scene, with the in-call overlay on screen.
## phone.incoming_call() and phone.dial() invoke it in a nested context, so
## the story (or the open phone) carries on where it was once it returns.
label phone_calls_session(_phone_call_who, _phone_call_uid, _phone_call_label):
    $ phone._begin_call(_phone_call_who, _phone_call_uid, label=True)
    call expression _phone_call_label
    $ phone.end_call()
    return
