from IContact_ren import IContact
from Message_ren import Message
from Reply_ren import Reply
from Messages_ren import messages
from MessagesService_ren import MessagesService

SetVariable: Callable[[str, Any], Any]

"""renpy
init python:
"""

from typing import Any, Callable, Optional


class MessageBuilder:
    def __init__(self, contact: "IContact", clear_pending: bool = False) -> None:
        self.contact: "IContact" = contact
        self.clear_pending: bool = clear_pending
        self.message_queue: list["Message"] = []
        self.current_message: Optional["Message"] = None
        self.functions: list[tuple[Callable[..., Any], tuple[Any], dict[str, Any]]] = []

    def __repr__(self) -> str:
        return f"MessageBuilder({self.contact})"

    def new_message(self, content: str, *replies: "Reply") -> "MessageBuilder":
        self.current_message = Message(self.contact, content, replies)
        self.message_queue.append(self.current_message)

        messages.move_contact_to_top(self.contact)

        return self

    def add_reply(
        self, content: str, next_message: Optional["MessageBuilder"] = None
    ) -> "MessageBuilder":
        self.add_replies(Reply(content, next_message))

        return self

    def add_replies(self, *replies: "Reply") -> "MessageBuilder":
        if self.current_message is None or self.current_message.replies:
            return self.new_message("", *replies)

        self.current_message.replies = replies

        return self

    def add_function(
        self, function: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> "MessageBuilder":
        self.functions.append((function, args, kwargs))

        return self

    def set_variable(self, var_name: str, value: Any) -> "MessageBuilder":
        self.add_function(SetVariable(var_name, value))

        return self

    def send(self) -> None:
        for function, args, kwargs in self.functions:
            function(*args, **kwargs)

        if self.clear_pending:
            self.contact.pending_text_messages.clear()

        # Add message queue to the start of pending messages
        self.contact.pending_text_messages[:0] = self.message_queue
        self.message_queue.clear()

        MessagesService.send_next_messages(self.contact)
