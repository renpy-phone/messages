## Tests for the Social app.

define _test_social_pal = phone.Contact("test_social_pal", "Pat", handle="pat.snaps")

init python:
    phone.social_profile("test_social_pal", bio="Film photos only.", followers=120, following=80)

    def _test_social_buttons(kind, screen=None):
        """Buttons in the open phone whose action class is `kind`."""
        rv = []
        seen = set()

        def walk(d):
            if d is None or id(d) in seen:
                return
            seen.add(id(d))
            if isinstance(d, renpy.display.behavior.Button):
                a = d.action
                if type(a).__name__ == kind and (screen is None or getattr(a, "screen", None) == screen):
                    rv.append(d)
            for c in d.visit() or ():
                walk(c)

        walk(renpy.get_screen("phone", layer=phone.cfg.layer))
        return rv

    def _test_social_scroll_to_end():
        """Scrolls every viewport in the open phone to the bottom."""
        seen = set()

        def walk(d):
            if d is None or id(d) in seen:
                return
            seen.add(id(d))
            if isinstance(d, renpy.display.viewport.Viewport):
                d.yadjustment.change(d.yadjustment.range)
            for c in d.visit() or ():
                walk(c)

        walk(renpy.get_screen("phone", layer=phone.cfg.layer))

    class _TestSocialSubclass(phone.SocialApp):
        toggles = 0

        def toggle_like(self, post_uid):
            _TestSocialSubclass.toggles += 1
            phone.SocialApp.toggle_like(self, post_uid)

default _test_social_aff = 0
default _test_social_name = "Sam"
default _test_social_uid = None
default _test_social_waited = 0.0


label test_social_feed_model:
    $ s = phone.social
    $ expect_eq(s.unseen(), 0, "a new game has no unseen posts")
    $ expect(not phone.contact("test_social_pal").known, "the contact starts unknown")

    $ a = s.post("test_social_pal", "demo photo beach", "First", likes=3, time="2h")
    $ b = s.post(lucy, "demo photo city", "Second, [_test_social_name]")
    $ expect_eq([p.uid for p in s.posts()], [b, a], "posts are newest first")
    $ expect_eq(s.get(b).who, "lucy", "authors are stored by contact id")
    $ expect_eq(s.get(b).caption, "Second, Sam", "captions are interpolated when posted")
    $ expect_eq(s.get(a).time, "2h", "time label")
    $ expect_eq(s.unseen(), 2, "posts by others are unseen")
    $ expect_eq(s.badge(), 2, "unseen posts show on the badge")
    $ expect(phone.contact("test_social_pal").known, "posting makes a contact known")

    $ mine = s.post(None, "demo photo cat", "Mine")
    $ expect_eq(s.unseen(), 2, "the player's own posts are never unseen")
    $ expect_eq([p.uid for p in s.posts_by(None)], [mine], "posts_by(None) is the player's posts")
    $ expect_eq([p.uid for p in s.posts_by(_test_social_pal)], [a], "posts_by accepts a Contact")
    $ expect_eq(s.posts_by("max"), [], "posts_by with no posts")
    $ expect(s.get(12345) is None, "get with an unknown uid")

    # Opening the feed marks everything seen.
    $ phone.show("social")
    $ expect_eq(s.unseen(), 0, "launching the feed marks posts seen")
    $ s.post("lucy", "demo photo cat", "While open")
    $ expect_eq(s.unseen(), 0, "posts arriving while the feed is shown are seen")
    $ phone.close()

    # Launching straight into a profile doesn't count as seeing the feed.
    $ s.post("lucy", "demo photo city", "Later")
    $ expect_eq(s.unseen(), 1, "posts arriving while closed are unseen")
    $ phone.show("social", "phone_social_profile", who="lucy")
    $ expect_eq(s.unseen(), 1, "a profile doesn't mark the feed seen")
    $ phone.Back()()
    # The feed marks posts seen from a timer once it is on screen; allow for
    # slow renders instead of relying on one short wait.
    $ _test_social_waited = 0.0
    while s.unseen() and _test_social_waited < 5.0:
        $ wait(0.1)
        $ _test_social_waited += 0.1
    $ expect_eq(s.unseen(), 0, "going back to the feed marks posts seen")
    $ phone.close()

    $ s.delete(mine)
    $ expect_eq(s.posts_by(None), [], "delete removes a post")
    return


label test_social_likes:
    $ s = phone.social
    $ _test_social_aff = 0
    $ uid = s.post("test_social_pal", "demo photo beach", likes=5, on_like=IncrementVariable("_test_social_aff"), notify=False)
    $ expect(not s.liked(uid), "posts start unliked")
    $ expect_eq(s.get(uid).like_count, 5, "base like count")

    $ phone.SocialToggleLike(uid)()
    $ expect(s.liked(uid), "the like button likes")
    $ expect_eq(s.get(uid).like_count, 6, "the player's like is counted")
    $ expect_eq(_test_social_aff, 1, "on_like runs on the first like")
    $ phone.SocialToggleLike(uid)()
    $ expect(not s.liked(uid), "the like button toggles")
    $ expect_eq(s.get(uid).like_count, 5, "unliking removes the player's like")
    $ phone.SocialToggleLike(uid)()
    $ expect_eq(_test_social_aff, 1, "on_like doesn't run again after unlike and like")

    # Script side.
    $ uid2 = s.post("lucy", "demo photo city", on_like=[IncrementVariable("_test_social_aff")], notify=False)
    $ s.like(uid2)
    $ expect(s.liked(uid2), "like() from script")
    $ expect_eq(_test_social_aff, 1, "script likes don't run on_like by default")
    $ s.unlike(uid2)
    $ expect(not s.liked(uid2), "unlike() from script")
    $ phone.SocialToggleLike(uid2)()
    $ expect_eq(_test_social_aff, 2, "a script like leaves on_like for the player's first like")
    $ phone.SocialToggleLike(uid2)()
    $ phone.SocialToggleLike(uid2)()
    $ expect_eq(_test_social_aff, 2, "and it still runs only once")

    # A script like on an already liked post, then the player toggles.
    $ uid4 = s.post("lucy", "demo photo cat", on_like=IncrementVariable("_test_social_aff"), notify=False)
    $ s.like(uid4)
    $ phone.SocialToggleLike(uid4)()
    $ expect(not s.liked(uid4), "the player can unlike a script like")
    $ phone.SocialToggleLike(uid4)()
    $ expect_eq(_test_social_aff, 3, "the player's first like after a script like runs on_like")
    $ _test_social_aff = 1

    $ uid3 = s.post("lucy", "demo photo cat", on_like=IncrementVariable("_test_social_aff"), notify=False)
    $ s.like(uid3, effects=True)
    $ s.like(uid3, effects=True)
    $ expect_eq(_test_social_aff, 2, "like(effects=True) runs on_like once")
    $ s.set_likes(uid3, 1000)
    $ expect_eq(s.get(uid3).like_count, 1001, "set_likes")
    $ expect(not s.liked(999999), "liked() with an unknown uid")
    return


label test_social_comments:
    $ s = phone.social
    $ _test_social_aff = 0
    $ shared = phone.CommentOption("Love it", IncrementVariable("_test_social_aff"))
    $ uid = s.post("lucy", "demo photo beach", comments=[("max", "Nice!"), (None, "Wow")], comment_options=[shared, "Cool", "Cool"], notify=False)
    $ p = s.get(uid)
    $ expect_eq([c.who for c in p.comments], ["max", None], "initial comments keep their authors")
    $ expect_eq(len(set(c.uid for c in p.comments)), 2, "comments get uids")
    $ opts = p.open_options()
    $ expect_eq([o.text for o in opts], ["Love it", "Cool", "Cool"], "comment options (strings allowed)")
    $ expect_eq(len(set(o.uid for o in opts)), 3, "options get distinct uids")

    $ phone.SocialUseOption(uid, opts[0].uid)()
    $ expect_eq((p.comments[-1].who, p.comments[-1].text), (None, "Love it"), "an option posts a player comment")
    $ expect_eq(_test_social_aff, 1, "option effects run")
    $ expect_eq(len(p.open_options()), 2, "a used option is gone")
    $ expect(not s.use_option(uid, opts[0].uid), "an option can only be used once")
    $ expect_eq(_test_social_aff, 1, "effects don't run twice")
    $ expect_eq(len(p.comments), 3, "no duplicate comment")

    # Options with the same text are separate.
    $ s.use_option(uid, opts[2].uid)
    $ expect_eq([o.uid for o in p.open_options()], [opts[1].uid], "options match by uid, not text")

    # The same CommentOption on another post is independent.
    $ uid2 = s.post("max", "demo photo city", comment_options=[shared], notify=False)
    $ expect_eq(len(s.get(uid2).open_options()), 1, "options are copied per post")

    $ cuid = s.comment(uid, "max", "Hey [_test_social_name]")
    $ expect_eq(p.comments[-1].text, "Hey Sam", "comment() interpolates")
    $ expect_eq(p.comments[-1].uid, cuid, "comment() returns the uid")
    $ s.comment(uid, None, "Thanks!")
    $ expect_eq(p.comments[-1].who, None, "the player can comment from script")
    return


label test_social_follow:
    $ s = phone.social
    $ base_following = s.following_count(None)
    $ expect(not s.following("test_social_pal"), "not following at start")
    $ expect_eq(s.followers("test_social_pal"), 120, "followers from the profile registry")
    $ expect_eq(s.following_count("test_social_pal"), 80, "following count from the registry")
    $ expect_eq(s.bio(_test_social_pal), "Film photos only.", "bio from the registry")

    $ phone.SocialToggleFollow("test_social_pal")()
    $ expect(s.following("test_social_pal"), "the follow button follows")
    $ expect_eq(s.followers("test_social_pal"), 121, "following adds the player to the followers")
    $ expect_eq(s.following_count(None), base_following + 1, "the player's following count")
    $ phone.SocialToggleFollow(_test_social_pal)()
    $ expect(not s.following("test_social_pal"), "the follow button toggles")
    $ expect_eq(s.followers("test_social_pal"), 120, "unfollowing")

    $ s.follow("test_social_pal")
    $ s.set_followers("test_social_pal", 5000)
    $ expect_eq(s.followers("test_social_pal"), 5001, "set_followers")
    $ s.unfollow("test_social_pal")
    $ s.set_bio("test_social_pal", "Digital now.")
    $ expect_eq(s.bio("test_social_pal"), "Digital now.", "set_bio")

    $ expect_eq((s.followers("nobody"), s.bio("nobody")), (0, ""), "no profile registered")
    $ expect_eq(s.handle(None), phone.player_handle(), "player handle")
    $ phone.set_player_name("Sam [_test_social_name]", handle="sam.[_test_social_name]")
    $ expect_eq((s.display_name(None), s.handle(None)), ("Sam Sam", "sam.Sam"), "set_player_name reaches the profile")
    python:
        if config.developer:
            try:
                phone.social_profile("test_social_pal", bio="Runtime")
                expect(False, "social_profile() at runtime is rejected")
            except Exception:
                pass
        with runtime_registry():
            phone.social_profile("test_social_runtime", bio="Runtime")
        expect_eq(s.bio("test_social_runtime"), "Runtime", "social_profile() inside runtime_registry")
        del phone.social_profiles["test_social_runtime"]
    $ expect_eq(s.handle("test_social_pal"), "pat.snaps", "contact handle")
    $ expect_eq([phone.social_count(n) for n in (950, 1284, 12400, 3100000)], ["950", "1,284", "12.4K", "3.1M"], "short counts")
    return


label test_social_pickle:
    python:
        from renpy.compat.pickle import dumps, loads
        s = phone.social
        uid = s.post("lucy", "demo photo beach", "Hi", likes=2, time="1h",
            comments=[("max", "Yo")], comment_options=[phone.CommentOption("Hey", [IncrementVariable("_test_social_aff")])],
            on_like=IncrementVariable("_test_social_aff"), notify=False)
        s.post(None, Solid("#f00"), "Displayable image")
        s.like(uid)
        s.follow("lucy")
        s.set_bio("lucy", "Changed")
        copy = loads(dumps(phone.social_state))
        expect_eq([p.uid for p in copy.posts], [p.uid for p in phone.social_state.posts], "posts survive pickling")
        cp = copy.posts[1]
        expect(cp.liked and not cp.like_effects_done, "like flags survive pickling")
        expect_eq([c.text for c in cp.comments], ["Yo"], "comments survive pickling")
        expect_eq(cp.options[0].text, "Hey", "options survive pickling")
        expect_eq(len(cp.options[0].effects), 1, "option effects survive pickling")
        expect_eq(copy.following, {"lucy": True}, "follows survive pickling")
        expect_eq(copy.bios, {"lucy": "Changed"}, "bios survive pickling")

        if config.developer:
            try:
                s.post("lucy", "demo photo cat", on_like=Function(lambda: None), notify=False)
                expect(False, "an unpicklable on_like is rejected")
            except TypeError:
                pass
            try:
                s.post("lucy", "demo photo cat", comment_options=[phone.CommentOption("x", Function(lambda: None))], notify=False)
                expect(False, "unpicklable option effects are rejected")
            except TypeError:
                pass
        expect_eq(len(phone.social_state.posts), 2, "rejected posts are not added")
    return


label test_social_load_more:
    $ s = phone.social
    $ old_max = phone.cfg.social_max_rendered
    $ phone.cfg.social_max_rendered = 3
    python:
        for i in range(7):
            s.post("lucy", "demo photo beach", "Post {}".format(i), notify=False)
    $ renpy.hide_screen("phone_notification", layer=phone.cfg.layer)
    $ phone.show("social")
    $ wait(0.2)
    $ expect_eq(len(_test_social_buttons("SocialToggleLike")), 3, "the feed builds only the first batch")
    $ more = _test_social_buttons("SetLocalVariable")
    $ expect_eq(len(more), 1, "the feed has a Load more button")
    $ _test_social_scroll_to_end()
    $ shot("social-load-more")
    $ more[0].action()
    $ wait(0.2)
    $ expect_eq(len(_test_social_buttons("SocialToggleLike")), 6, "Load more adds a batch")
    $ _test_social_buttons("SetLocalVariable")[0].action()
    $ wait(0.2)
    $ expect_eq(len(_test_social_buttons("SocialToggleLike")), 7, "Load more stops at the last post")
    $ expect_eq(_test_social_buttons("SetLocalVariable"), [], "no Load more once everything is shown")

    $ phone.Navigate("phone_social_profile", who="lucy")()
    $ wait(0.2)
    $ expect_eq(len(_test_social_buttons("Navigate", "phone_social_post")), 3, "the profile grid builds the first batch")
    $ _test_social_buttons("SetLocalVariable")[0].action()
    $ wait(0.2)
    $ expect_eq(len(_test_social_buttons("Navigate", "phone_social_post")), 6, "the grid loads more")
    $ phone.close()
    $ phone.cfg.social_max_rendered = old_max
    return


label test_social_memo_and_saves:
    $ s = phone.social
    $ a = phone.social_icon_states("social/like", 30)
    $ expect(a is phone.social_icon_states("social/like", 30), "icons are memoized")
    $ expect(a is not phone.social_icon_states("social/like", 31), "the memo is keyed on the size")
    $ phone.set_theme("dark")
    $ expect(a is not phone.social_icon_states("social/like", 30), "the memo is keyed on the theme")
    $ phone.set_theme("light")

    # The heart is an outline until liked, then filled; every state has art,
    # with dark versions of the themed ones.
    python:
        for name, states in (("social/like", ("idle", "hover", "selected_idle", "selected_hover")),
                             ("social/comment", ("idle", "hover")),
                             ("social/profile_ring", ("idle", "hover")),
                             ("social/follow_button", ("idle", "hover", "selected_idle", "selected_hover")),
                             ("social/option_button", ("idle", "hover"))):
            for theme, folder in (("light", ""), ("dark", "themes/dark/")):
                phone.set_theme(theme)
                for st in states:
                    expect_eq(phone.art_path(name, st), "gui/phone/{}{}_{}.png".format(folder, name, st), "{} {} {} art".format(theme, name, st))
        phone.set_theme("light")
        expect_eq(phone.art_path("apps/social/icon", "hover"), "gui/phone/apps/social/icon_hover.png", "the app icon has a hover state")
        expect(not hasattr(phone.social, "glyph"), "the app draws its icon from art")

    # Saves from before a field existed fall back to class defaults.
    $ uid = s.post("lucy", "demo photo beach", comment_options=["Hi"], comments=[("max", "Yo")], notify=False)
    $ p = s.get(uid)
    python:
        for obj, field in ((p, "seen"), (p, "like_effects_done"), (p.comments[0], "text"), (p.options[0], "used")):
            delattr(obj, field)
    $ expect_eq((p.seen, p.like_effects_done, p.comments[0].text, p.options[0].used), (True, False, "", False), "missing fields use class defaults")
    $ delattr(phone.social_state, "bios")
    $ phone._social_after_load()
    $ s.set_bio("lucy", "Loaded")
    $ expect_eq(phone.social_state.bios, {"lucy": "Loaded"}, "after_load restores missing state fields")
    $ expect(not hasattr(phone.SocialState, "bios"), "no shared class-level dict")

    # A game can replace the app with a subclass; actions look it up by id.
    $ original = phone.apps["social"]
    $ phone.apps["social"] = _TestSocialSubclass()
    $ phone.SocialToggleLike(uid)()
    $ expect_eq(_TestSocialSubclass.toggles, 1, "actions use the registered app")
    $ phone.apps["social"] = original
    return


label _test_social_fill:
    $ s = phone.social
    $ s.post(None, "demo photo cat", "Meet the boss of the house.", likes=11, time="2d", comments=[("lucy", "THE BOSS")], notify=False)
    $ s.post("test_social_pal", "demo photo cat", "", likes=0, notify=False)
    $ s.post("max", "demo photo city", "City lights never get old.", likes=87, time="5h", comments=[("eileen", "Where is this?"), ("max", "Rooftop downtown!"), ("lucy", "Take me next time")], notify=False)
    $ _test_social_uid = s.post("lucy", "demo photo beach", "Sun, sand and zero deadlines. Back to the sketchbook tomorrow, promise.", likes=1283, time="1h",
        comments=[("max", "Jealous."), ("eileen", "Gorgeous colors!")],
        comment_options=[phone.CommentOption("You look so happy here!"), phone.CommentOption("Sunburn incoming.")])
    return


label test_social_screens:
    $ s = phone.social
    $ renpy.hide_screen("phone_notification", layer=phone.cfg.layer)
    $ phone.show("social")
    $ shot("social-empty")
    $ phone.close()

    call _test_social_fill
    $ renpy.hide_screen("phone_notification", layer=phone.cfg.layer)
    $ uid = _test_social_uid
    $ phone.show()
    $ shot("social-home-badge")
    $ phone.Launch("social")()
    $ phone.Navigate("phone_social_post", post=uid)()
    $ phone.Back()()
    $ s.like(uid)
    $ shot("social-feed")
    $ phone.Navigate("phone_social_post", post=uid)()
    $ shot("social-post")
    $ phone.SocialUseOption(uid, s.get(uid).options[0].uid)()
    $ shot("social-post-commented")
    $ phone.Navigate("phone_social_profile", who="lucy")()
    $ shot("social-profile")
    $ phone.SocialToggleFollow("lucy")()
    $ shot("social-profile-following")
    $ phone.Navigate("phone_social_profile", who=None)()
    $ shot("social-own-profile")
    $ phone.Navigate("phone_social_profile", who="eileen")()
    $ shot("social-profile-empty")
    $ phone.Navigate("phone_image_viewer", image=s.get(uid).image)()
    $ shot("social-viewer")
    $ phone.Navigate("phone_social_post", post=99999)()
    $ shot("social-post-missing")

    $ phone.set_theme("dark")
    $ phone.Launch("social")()
    $ shot("social-feed-dark")
    $ phone.Navigate("phone_social_post", post=uid)()
    $ shot("social-post-dark")
    $ phone.Navigate("phone_social_profile", who="lucy")()
    $ shot("social-profile-dark")
    $ phone.set_theme("light")
    $ phone.close()
    return
