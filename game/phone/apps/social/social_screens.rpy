# Screens of the Social app: the feed, a single post and profiles.

## The feed: every post, newest first.
screen phone_social():
    # Only the newest posts are built; "Load more" adds another batch. The
    # name is unique because the shell reuses one scope for every app screen.
    default social_feed_shown = phone.cfg.social_max_rendered
    $ posts = phone.social_state.posts

    # Posts that arrive while the feed is on screen count as seen.
    if phone.social.unseen():
        timer 0.05 action phone.SocialMarkSeen()

    vbox:
        frame:
            style "phone_header"

            text phone.social.name style "phone_social_logo" xpos phone.px(6)

            button:
                style "phone_social_header_button"
                xalign 1.0
                action phone.Navigate("phone_social_profile", who=None)
                alt _("Your profile")
                add phone.avatar(None, phone.px(40))

        use phone_divider

        frame:
            style "phone_body"
            background phone.color("surface")

            if posts:
                use phone_list:
                    for p in posts[:social_feed_shown]:
                        use phone_social_card(p)
                    if len(posts) > social_feed_shown:
                        use phone_social_load_more(SetLocalVariable("social_feed_shown", social_feed_shown + phone.cfg.social_max_rendered))
            else:
                use phone_empty(_("No posts yet.\nWhen people you follow share\nphotos, you'll see them here."))


## One post. `full` shows it on its own page, where every comment is listed
## below it instead of a summary.
screen phone_social_card(p, full=False):
    $ width = phone.social_card_width()
    $ pad = phone.px(14)
    $ handle = phone.social.handle(p.who)
    $ count = p.like_count
    $ ncomments = len(p.comments)

    frame:
        style "phone_social_card"

        vbox:
            button:
                style "phone_social_author"
                action phone.Navigate("phone_social_profile", who=p.who)
                alt phone.social.handle(p.who)

                hbox:
                    spacing phone.px(12)
                    add phone.avatar(p.who, phone.px(40)) yalign 0.5
                    vbox:
                        yalign 0.5
                        text phone.social.handle(p.who) style "phone_social_handle" substitute False
                        if p.time:
                            text p.time style "phone_social_meta" substitute False

            button:
                style "empty"
                action phone.Navigate("phone_image_viewer", image=p.image)
                alt _("View photo")
                add phone.cover(p.image, width, width)

            frame:
                style "empty"
                padding (pad - phone.px(6), phone.px(4), 0, 0)

                hbox:
                    spacing phone.px(2)

                    button:
                        style "phone_social_icon_button"
                        action phone.SocialToggleLike(p.uid)
                        alt (_("Unlike") if p.liked else _("Like"))
                        if p.liked:
                            add phone.social_icon("heart", "social_like", phone.px(30))
                        else:
                            add phone.social_icon("heart_outline", "text", phone.px(30))

                    button:
                        style "phone_social_icon_button"
                        action (NullAction() if full else phone.Navigate("phone_social_post", post=p.uid))
                        alt _("Comments")
                        add phone.social_icon("comment", "text", phone.px(29))

            frame:
                style "empty"
                padding (pad, 0)
                xfill True

                vbox:
                    spacing phone.px(4)
                    xsize width - 2 * pad

                    text (_("1 like") if count == 1 else _("{} likes").format(phone.social_count(count))):
                        style "phone_social_text"
                        bold True
                        substitute False

                    if p.caption:
                        text "{b}[handle!q]{/b} [p.caption]" style "phone_social_text"

                    if not full:
                        if ncomments:
                            button:
                                style "phone_social_link"
                                action phone.Navigate("phone_social_post", post=p.uid)
                                text (_("View 1 comment") if ncomments == 1 else _("View all {} comments").format(ncomments)):
                                    style "phone_social_link_text"
                                    substitute False
                            for c in p.comments[-2:]:
                                $ chandle = phone.social.handle(c.who)
                                text "{b}[chandle!q]{/b} [c.text]" style "phone_social_text"
                        elif p.open_options():
                            button:
                                style "phone_social_link"
                                action phone.Navigate("phone_social_post", post=p.uid)
                                text _("Add a comment…") style "phone_social_link_text"


## A single post with all its comments and the player's comment options.
screen phone_social_post(post):
    $ p = phone.social.get(post)

    use phone_page(_("Post")):
        if p is None:
            use phone_empty(_("This post is no longer available."))
        else:
            $ pad = phone.px(14)
            $ options = p.open_options()

            add phone.color("surface")

            # The player's comment options stay pinned below the scrolling post.
            side ("c b" if options else "c"):
                use phone_list:
                    use phone_social_card(p, full=True)
                    use phone_divider

                    frame:
                        style "empty"
                        background phone.color("surface")
                        padding (pad, phone.px(14))
                        xfill True

                        vbox:
                            spacing phone.px(14)
                            xsize phone.social_card_width() - 2 * pad

                            if not p.comments:
                                text _("No comments yet.") style "phone_social_meta"

                            for c in p.comments:
                                $ chandle = phone.social.handle(c.who)
                                hbox:
                                    spacing phone.px(12)
                                    button:
                                        style "empty"
                                        action phone.Navigate("phone_social_profile", who=c.who)
                                        alt phone.social.handle(c.who)
                                        add phone.avatar(c.who, phone.px(34))
                                    text "{b}[chandle!q]{/b} [c.text]":
                                        style "phone_social_text"
                                        yalign 0.5
                                        xsize phone.social_card_width() - 2 * pad - phone.px(46)

                if options:
                    vbox:
                        use phone_divider
                        frame:
                            style "phone_social_reply_panel"
                            vbox:
                                spacing phone.px(8)
                                text _("Leave a comment") style "phone_social_section"
                                for o in options:
                                    button:
                                        style "phone_social_option_button"
                                        action phone.SocialUseOption(p.uid, o.uid)
                                        text o.text style "phone_social_option_button_text" substitute False


## A profile: `who` is a contact id, or None for the player.
screen phone_social_profile(who=None):
    default social_grid_shown = phone.cfg.social_max_rendered
    $ posts = phone.social.posts_by(who)
    $ width = phone.social_card_width()
    $ pad = phone.px(16)
    $ gap = phone.px(3)
    $ cell = (width - 2 * gap) // 3
    $ avatar_size = phone.px(88)
    $ bio = phone.social.bio(who)
    $ stat_width = (width - 2 * pad - avatar_size - phone.px(8)) // 3

    use phone_page(phone.social.handle(who)):
        add phone.color("surface")

        use phone_list:
            frame:
                style "empty"
                background phone.color("surface")
                padding (pad, pad)
                xfill True

                vbox:
                    spacing phone.px(10)

                    hbox:
                        add phone.avatar(who, avatar_size) yalign 0.5
                        null width phone.px(8)

                        for number, label in ((len(posts), _("posts")), (phone.social.followers(who), _("followers")), (phone.social.following_count(who), _("following"))):
                            vbox:
                                xsize stat_width
                                yalign 0.5
                                text phone.social_count(number) style "phone_social_count"
                                text label style "phone_social_count_label"

                    text phone.social.display_name(who) style "phone_social_handle" substitute False

                    if bio:
                        text bio style "phone_social_text" substitute False xsize width - 2 * pad

                    if who is not None:
                        button:
                            style "phone_social_follow_button"
                            xfill True
                            action phone.SocialToggleFollow(who)
                            text (_("Following") if phone.social.following(who) else _("Follow")):
                                style "phone_social_follow_button_text"

            use phone_divider

            if posts:
                hbox:
                    xsize width
                    box_wrap True
                    spacing gap
                    box_wrap_spacing gap

                    for p in posts[:social_grid_shown]:
                        button:
                            style "phone_social_tile"
                            xysize (cell, cell)
                            action phone.Navigate("phone_social_post", post=p.uid)
                            alt _("Photo")
                            add phone.cover(p.image, cell, cell)
                if len(posts) > social_grid_shown:
                    use phone_social_load_more(SetLocalVariable("social_grid_shown", social_grid_shown + phone.cfg.social_max_rendered))
            else:
                fixed:
                    xsize width
                    ysize phone.px(200)
                    text _("No posts yet.") style "phone_empty_text"


## The button at the end of a list that builds the next batch of posts.
screen phone_social_load_more(action):
    frame:
        style "empty"
        padding (phone.px(14), phone.px(14))
        xfill True
        button:
            style "phone_social_option_button"
            action action
            text _("Load more") style "phone_social_option_button_text" xalign 0.5
