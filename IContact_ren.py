from Message_ren import Message

"""renpy
init python:
"""

from abc import ABC


class IContact(ABC):
    def __init__(self) -> None:
        self.text_messages: list[Message] = []
        self.pending_text_messages: list[Message] = []
