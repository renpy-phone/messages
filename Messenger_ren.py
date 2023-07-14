from IContact_ren import IContact
from MessengerService_ren import MessengerService

"""renpy
init python:
"""


class Messenger:
    def __init__(self) -> None:
        self.name: str = "Messenger"
        self.home_screen = "messenger_home"

        self.contacts: list["IContact"] = []

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.name})"

    @property
    def image(self) -> str:
        if self.notification:
            return f"{self.name.lower()}_icon_notification"
        else:
            return f"{self.name.lower()}_icon"

    @property
    def notification(self) -> bool:
        return any(MessengerService.has_replies(contact) for contact in self.contacts)

    def move_contact_to_top(self, contact: "IContact") -> None:
        try:
            self.contacts.insert(0, self.contacts.pop(self.contacts.index(contact)))
        except ValueError:
            self.contacts.insert(0, contact)


messenger: Messenger
