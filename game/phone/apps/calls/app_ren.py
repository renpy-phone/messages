"""renpy
init -910 python in phone:
"""

# Registers the Phone (calls) app.


class CallsApp(App):
    id = "calls"
    name = store._("Phone")
    screen = "phone_calls"
    order = 20

    def badge(self):
        s = globals().get("calls_state")
        return s.unseen_missed if s is not None else 0

    def on_launch(self, **kwargs):
        # Opening the app on the Recents tab shows the missed calls.
        if "who" not in kwargs and kwargs.get("tab", "recents") == "recents":
            mark_calls_seen()

    def reset(self):
        global calls_state
        calls_state = CallsState()


register_app(CallsApp())
