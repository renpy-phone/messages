"""renpy
init -920 python in phone:
"""

# Social: an Instagram-style photo feed.
#
# Scripts post through the app instance, `phone.social`:
#
#     $ uid = phone.social.post("lucy", "lucy beach", "Beach day!", likes=42,
#           on_like=IncrementVariable("lucy_affection"),
#           comment_options=[phone.CommentOption("So pretty!", IncrementVariable("lucy_affection"))])
#
# The API: post, comment, like / unlike / liked, follow / unfollow / following,
# posts_by, get, delete, set_likes, set_followers, set_bio. Screens use the
# actions SocialToggleLike, SocialUseOption and SocialToggleFollow.
#
# Static profile info (bio, follower counts) is registered at init time:
#
#     define lucy_profile = phone.social_profile("lucy", bio="I draw things.", followers=1280)
#
# Rename the app from an init block: `init python: phone.social.name = "Snapgram"`.

import store


# Art under gui/phone/ (placeholders from tools/art/social_art.rpy); lint
# reports any that is missing. The like heart is outlined when idle and
# filled when selected (liked).
require_art(
    "apps/social/icon",
    "social/like",
    "social/comment",
    "social/profile_ring",
    "social/follow_button",
    "social/option_button",
)

cfg.sounds.setdefault("social_post", None)
cfg.sounds.setdefault("social_like", None)

# How many posts the feed (and a profile grid) builds before the player taps
# "Load more". Keeps the screens fast in long playthroughs.
if not hasattr(cfg, "social_max_rendered"):
    cfg.social_max_rendered = 30


# Static profile registry -----------------------------------------------------

social_profiles = {}  # contact id (None for the player) -> SocialProfile


class SocialProfile(python_object):
    """Static profile info for a contact, or for the player (who=None).

    `followers` does not include the player, who adds one by following.
    `followed` is whether the player follows this account from the start.
    """

    def __init__(self, who, bio="", followers=0, following=0, followed=False):
        self.who = contact_id(who)
        self.bio = bio
        self.followers = followers
        self.following = following
        self.followed = followed


def social_profile(who, bio="", followers=0, following=0, followed=False):
    """Registers profile defaults for `who` (a Contact, an id, or None for the player)."""
    init_only("phone.social_profile()")
    rv = SocialProfile(who, bio=bio, followers=followers, following=following, followed=followed)
    social_profiles[rv.who] = rv
    return rv


_SOCIAL_NO_PROFILE = SocialProfile(None)


def _social_static(who):
    return social_profiles.get(contact_id(who), _SOCIAL_NO_PROFILE)


# Saved state -----------------------------------------------------------------

# Saved classes give every field a class-level default, so saves made before
# a field was added still load (the missing attribute falls back to it).
# Mutable fields default to immutable empties and are always set in __init__.

class CommentOption(object):
    """A comment the player can post on a post, once.

    `effects` is a Ren'Py action or a list of them, run when the player
    posts this comment.
    """

    text = ""
    effects = ()
    uid = None
    used = False

    def __init__(self, text, effects=None):
        self.text = text
        self.effects = as_list(effects)
        self.uid = None
        self.used = False

    def __repr__(self):
        return "<phone.CommentOption {!r}>".format(self.text)


class SocialComment(object):
    uid = None
    who = None
    text = ""

    def __init__(self, uid, who, text):
        self.uid = uid
        self.who = who  # contact id, or None for the player
        self.text = text


class SocialPost(object):
    uid = None
    who = None
    image = None
    caption = ""
    likes = 0
    liked = False
    like_effects = ()
    like_effects_done = False
    comments = ()
    options = ()
    time = None
    seen = True

    def __init__(self, uid, who, image, caption="", likes=0, time=None):
        self.uid = uid
        self.who = who  # contact id, or None for the player
        self.image = image
        self.caption = caption
        self.likes = likes  # likes from other people
        self.liked = False  # liked by the player
        self.like_effects = []
        self.like_effects_done = False
        self.comments = []
        self.options = []
        self.time = time
        self.seen = True

    @property
    def like_count(self):
        return self.likes + (1 if self.liked else 0)

    def open_options(self):
        """Comment options the player has not used yet."""
        return [o for o in self.options if not o.used]


class SocialState(object):
    # Missing fields are filled in by _social_after_load instead of class
    # defaults, so no save ever shares a mutable class-level dict.
    version = 1

    def __init__(self):
        self.version = 1
        self.posts = []  # newest first
        self.followers = {}  # who -> follower count, overrides the profile
        self.following = {}  # who -> bool, whether the player follows them
        self.bios = {}  # who -> bio, overrides the profile


def _social_after_load():
    s = globals().get("social_state")
    if s is None:
        return
    for k, v in SocialState().__dict__.items():
        if k not in s.__dict__:
            setattr(s, k, v)


# The app and its script API ---------------------------------------------------

class SocialApp(App):
    id = "social"
    name = _("Photogram")
    screen = "phone_social"
    order = 30

    CommentOption = CommentOption

    def reset(self):
        global social_state
        social_state = SocialState()

    def badge(self):
        return self.unseen()

    def on_launch(self, **kwargs):
        if state.current()[0] == self.screen:
            self.mark_seen()

    # Posts -------------------------------------------------------------------

    def post(self, who, image, caption="", likes=0, comments=(), comment_options=(),
             on_like=None, time=None, notify=True):
        """Adds a post to the top of the feed and returns its uid.

        `who` is a Contact, a contact id, or None for the player. `image` is a
        displayable or an image name. `comments` is a list of (who, text).
        `comment_options` is a list of CommentOption (or plain strings) the
        player can post. `on_like` is an action or list of actions run the
        first time the player likes the post. `time` is a free-form label,
        such as "2h" or "Yesterday".
        """
        who = contact_id(who)
        p = SocialPost(state.next_uid(), who, image, renpy.substitute(caption), likes, time)

        effects = as_list(on_like)
        check_picklable(effects, "on_like")
        check_picklable(image, "The post image")
        p.like_effects = effects

        for c_who, text in comments:
            p.comments.append(SocialComment(state.next_uid(), contact_id(c_who), renpy.substitute(text)))

        for o in comment_options:
            if not isinstance(o, CommentOption):
                o = CommentOption(o)
            check_picklable(o.effects, "CommentOption effects")
            copy = CommentOption(renpy.substitute(o.text), o.effects)
            copy.uid = state.next_uid()
            p.options.append(copy)

        p.seen = who is None or is_showing(self.screen)
        social_state.posts.insert(0, p)

        if who is not None:
            add_contact(who)
            if notify:
                _social_notify(__("{} posted a photo").format(contact(who).name), "social_post")
        return p.uid

    def get(self, post_uid):
        """The post with this uid, or None."""
        for p in social_state.posts:
            if p.uid == post_uid:
                return p
        return None

    def _get(self, post_uid):
        p = self.get(post_uid)
        if p is None:
            raise Exception("phone.social: no post with uid {!r}.".format(post_uid))
        return p

    def posts(self):
        return list(social_state.posts)

    def posts_by(self, who):
        """Posts by `who` (None for the player), newest first."""
        who = contact_id(who)
        return [p for p in social_state.posts if p.who == who]

    def delete(self, post_uid):
        social_state.posts = [p for p in social_state.posts if p.uid != post_uid]

    def unseen(self):
        """Number of posts by others the player has not seen in the feed."""
        return sum(1 for p in social_state.posts if not p.seen)

    def mark_seen(self):
        for p in social_state.posts:
            if not p.seen:
                p.seen = True

    # Comments ----------------------------------------------------------------

    def comment(self, post_uid, who, text, notify=True):
        """Adds a comment by `who` (None for the player). Returns its uid."""
        p = self._get(post_uid)
        c = SocialComment(state.next_uid(), contact_id(who), renpy.substitute(text))
        p.comments.append(c)
        if notify and c.who is not None and p.who is None:
            _social_notify(__("{} commented: {}").format(contact(c.who).name, c.text))
        return c.uid

    def use_option(self, post_uid, option_uid):
        """Posts one of the player's comment options, once. True if it was posted."""
        p = self._get(post_uid)
        for o in p.options:
            if o.uid == option_uid:
                if o.used:
                    return False
                o.used = True
                p.comments.append(SocialComment(state.next_uid(), None, o.text))
                run_effects(o.effects)
                return True
        return False

    # Likes -------------------------------------------------------------------

    def like(self, post_uid, effects=False):
        """Makes the player like a post.

        With effects=True the post's on_like effects run, unless they already
        have. With the default effects=False they are left for later, so
        the player's own first like still runs them.
        """
        p = self._get(post_uid)
        p.liked = True
        if effects and not p.like_effects_done:
            p.like_effects_done = True
            run_effects(p.like_effects)

    def unlike(self, post_uid):
        self._get(post_uid).liked = False

    def liked(self, post_uid):
        p = self.get(post_uid)
        return bool(p and p.liked)

    def toggle_like(self, post_uid):
        """What the like button does: on_like effects run the first time only."""
        p = self._get(post_uid)
        if p.liked:
            self.unlike(post_uid)
        else:
            play_sound("social_like")
            self.like(post_uid, effects=True)

    def set_likes(self, post_uid, likes):
        """Changes the like count from other people."""
        self._get(post_uid).likes = likes

    # Profiles ----------------------------------------------------------------

    def follow(self, who):
        social_state.following[contact_id(who)] = True

    def unfollow(self, who):
        social_state.following[contact_id(who)] = False

    def following(self, who):
        """True if the player follows `who`."""
        who = contact_id(who)
        return social_state.following.get(who, _social_static(who).followed)

    def followers(self, who):
        """Follower count of `who` (None for the player), including the player."""
        who = contact_id(who)
        n = social_state.followers.get(who, _social_static(who).followers)
        if who is not None and self.following(who):
            n += 1
        return n

    def set_followers(self, who, count):
        """Changes the follower count of `who`, not counting the player."""
        social_state.followers[contact_id(who)] = count

    def following_count(self, who):
        """How many accounts `who` follows."""
        who = contact_id(who)
        n = _social_static(who).following
        if who is None:
            ids = set(social_state.following) | set(social_profiles)
            n += sum(1 for c in ids if c is not None and self.following(c))
        return n

    def bio(self, who):
        who = contact_id(who)
        return social_state.bios.get(who, _social_static(who).bio)

    def set_bio(self, who, text):
        social_state.bios[contact_id(who)] = text

    # Display helpers ----------------------------------------------------------

    def handle(self, who):
        if who is None:
            return player_handle()
        return contact(who).handle

    def display_name(self, who):
        if who is None:
            return player_name()
        return contact(who).name


def social_app():
    """The registered Social app, which may be a game's SocialApp subclass."""
    return get_app("social")


def _social_notify(text, sound="notification"):
    app = social_app()
    if not cfg.sounds.get(sound):
        sound = "notification"
    notify(__(app.name), text, app_id=app.id, sound=sound)


def social_count(n):
    """Short number for counters: 950, 12.4K, 3.1M."""
    for limit, unit, suffix in ((1000000, 1000000, "M"), (10000, 1000, "K")):
        if n >= limit:
            v = n / float(unit)
            return ("{:.1f}".format(v).rstrip("0").rstrip(".")) + suffix
    if n >= 1000:
        return "{:,}".format(n)
    return str(n)


@memoized
def social_icon_states(name, size):
    """Imagebutton states of one of the app's icons ("social/like",
    "social/comment"), `size` pixels square. Built once per theme, text size
    and resolution."""
    return art_states(name, (size, size))


def social_card_width():
    """Width of a feed card: the content width minus the list's scrollbar."""
    return content_size()[0] - px(4)


# Screen actions ------------------------------------------------------------

class SocialToggleLike(PhoneAction):
    def __init__(self, post_uid):
        self.post_uid = post_uid

    def run(self):
        social_app().toggle_like(self.post_uid)

    def get_selected(self):
        return social_app().liked(self.post_uid)


class SocialUseOption(PhoneAction):
    def __init__(self, post_uid, option_uid):
        self.post_uid = post_uid
        self.option_uid = option_uid

    def run(self):
        social_app().use_option(self.post_uid, self.option_uid)


class SocialToggleFollow(PhoneAction):
    def __init__(self, who):
        self.who = contact_id(who)

    def run(self):
        app = social_app()
        if app.following(self.who):
            app.unfollow(self.who)
        else:
            app.follow(self.who)

    def get_selected(self):
        return social_app().following(self.who)


class SocialMarkSeen(PhoneAction):
    def run(self):
        social_app().mark_seen()


"""renpy
default phone.social_state = phone.SocialState()

init -910 python in phone:
"""

# `phone.social` is the app instance scripts and screens talk to. A game can
# replace it with a subclass from its own init code:
#
#     init python:
#         class MySocial(phone.SocialApp):
#             name = "Snapgram"
#         phone.register_app(MySocial())
#
# The block at init 905 below points `phone.social` at whatever ended up
# registered, and the screen actions always look the app up by id.
social = register_app(SocialApp())

if _social_after_load not in store.config.after_load_callbacks:
    store.config.after_load_callbacks.append(_social_after_load)


"""renpy
init 905 python in phone:
"""

social = get_app("social")
