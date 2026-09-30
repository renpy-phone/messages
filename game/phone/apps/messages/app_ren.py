"""renpy
init -910 python in phone:
"""

# Registers the Messages app.


class MessagesApp(App):
    id = "messages"
    name = _("Messages")
    screen = "phone_messages"
    order = 10

    def badge(self):
        s = globals().get("messages_state")
        return s.badge() if s is not None else 0

    def on_launch(self, thread=None, **kwargs):
        if thread is not None:
            mark_read(thread)

    def reset(self):
        global messages_state
        messages_state = MessagesState()


register_app(MessagesApp())
