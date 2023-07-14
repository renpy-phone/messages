from Message_ren import Message

"""renpy
init -100 python:
"""

from abc import ABC


class IContact(ABC):
    def __init__(self, profile_picture: str) -> None:
        self.profile_picture: str = profile_picture

        self.text_messages: list[Message] = []
        self.pending_text_messages: list[Message] = []
