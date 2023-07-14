from IContact_ren import IContact
from Reply_ren import Reply
from MessageBuilder_ren import MessageBuilder
from Message_ren import Message
from Messages_ren import messages

"""renpy
init python:
"""

from typing import Optional


class MessagesService:
    @staticmethod
    def has_replies(contact: "IContact") -> bool:
        try:
            return bool(contact.text_messages[-1].replies)
        except (IndexError, AttributeError):
            return False

    @staticmethod
    def send_next_messages(contact: "IContact") -> None:
        while contact.pending_text_messages and not MessagesService.has_replies(
            contact
        ):
            contact.pending_text_messages.pop(0).send()

    @staticmethod
    def new_message(
        contact: "IContact",
        content: str,
        *replies: "Reply",
    ) -> None:
        contact.pending_text_messages.append(Message(contact, content, replies))

        messages.move_contact_to_top(contact)

        MessagesService.send_next_messages(contact)

    @staticmethod
    def add_reply(
        contact: "IContact",
        content: str,
        next_message: Optional["MessageBuilder"] = None,
    ) -> None:
        MessagesService.add_replies(contact, Reply(content, next_message))

    @staticmethod
    def add_replies(contact: "IContact", *replies: "Reply") -> None:
        if (
            not contact.pending_text_messages
            or contact.pending_text_messages[0].replies
        ):
            return MessagesService.new_message(contact, "", *replies)

        contact.pending_text_messages[-1].replies = replies

    @staticmethod
    def find_message(contact: "IContact", content: str) -> Optional["Message"]:
        for message in contact.pending_text_messages + contact.text_messages:
            if message.content == content:
                return message

        return None
