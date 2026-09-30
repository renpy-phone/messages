## Runs a call label as part of the story, with the in-call pill on screen.
## phone.incoming_call() and phone.dial() call it with renpy.call(); see the
## notes at the top of calls_ren.py for where the story continues.
label phone_calls_session(_phone_call_who, _phone_call_uid, _phone_call_label, _phone_call_reopen=None):
    $ phone.close()
    $ phone._begin_call(_phone_call_who, _phone_call_uid, label=True)
    call expression _phone_call_label
    $ phone._session_end(_phone_call_reopen)
    return
