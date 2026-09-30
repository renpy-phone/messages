"""renpy
init -970 python in phone:
"""

# Contacts are static definitions (use `define`). Anything that changes during
# the story, like a contact becoming known or being renamed, is saved in
# phone.state instead, keyed by the contact's id.

contacts = {}  # id -> Contact, in definition order


class Contact(python_object):
    """A person the player can text, call or follow.

    `id`
        A unique, stable string. Saves refer to contacts by id, so never
        change it once the game has shipped.
    `name`
        Display name. Text interpolation is applied, so "[mc_sister]" works.
        Defaults to the name of `character` when that is given.
    `avatar`
        Any displayable. When None, a colored circle with the initial is used.
    `character`
        Optional Ren'Py Character, used for the name and for phone calls.
    `number`, `handle`
        Shown by the Phone and Social apps.
    `call_label`
        Label called when the player phones this contact. Can be changed per
        save with phone.set_call_label().
    `known`
        Whether the contact starts in the address book. Contacts also become
        known when they text, call or post.
    """

    def __init__(self, id, name=None, avatar=None, character=None, number=None,
                 handle=None, color=None, call_label=None, known=False):
        init_only("phone.Contact()")
        if id in contacts and contacts[id] is not self:
            raise Exception("phone.Contact id {!r} is defined twice.".format(id))

        self.id = id
        self._name = name
        self._avatar = avatar
        self.character = character
        self.number = number
        self.handle = handle if handle is not None else id
        self.color = color
        self.call_label = call_label
        self.known_by_default = known

        contacts[id] = self

    # Saved state refers back to the registry, so a loaded save always sees
    # the same Contact object the scripts defined.
    def __reduce__(self):
        return (contact, (self.id,))

    def __repr__(self):
        return "<phone.Contact {}>".format(self.id)

    def _data(self):
        # phone.state only exists once the game has started.
        s = globals().get("state")
        if s is None:
            return {}
        return s.contact_data.get(self.id, {})

    @property
    def name(self):
        rv = self._data().get("name")
        if rv is None:
            rv = self._name
        if rv is None and self.character is not None:
            rv = self.character.name
        if rv is None:
            rv = self.id
        return renpy.substitute(rv)

    @property
    def avatar(self):
        rv = self._data().get("avatar")
        if rv is None:
            rv = self._avatar
        return rv

    @property
    def known(self):
        return self._data().get("known", self.known_by_default)

    @property
    def label(self):
        """The label called when the player phones this contact."""
        return self._data().get("call_label", self.call_label)

    def initial(self):
        n = self.name.strip()
        return n[:1].upper() if n else "?"

    def tint(self):
        """A stable color for placeholder avatars."""
        if self.color:
            return self.color
        palette = ["#ff6b6b", "#f59f00", "#51cf66", "#339af0", "#845ef7", "#f06595", "#20c997", "#fd7e14"]
        return palette[sum(ord(c) for c in self.id) % len(palette)]


class _MissingContact(Contact):
    pass


def contact(id_or_contact):
    """Looks up a contact by id. Accepts a Contact and returns it unchanged."""
    if isinstance(id_or_contact, Contact):
        return id_or_contact
    rv = contacts.get(id_or_contact)
    if rv is None:
        # A save refers to a contact the current scripts no longer define.
        rv = python_object.__new__(_MissingContact)
        rv.__dict__.update(
            id=id_or_contact, _name=id_or_contact, _avatar=None, character=None,
            number=None, handle=id_or_contact, color="#888888", call_label=None,
            known_by_default=False,
        )
    return rv


def contact_id(id_or_contact):
    if isinstance(id_or_contact, Contact):
        return id_or_contact.id
    return id_or_contact
