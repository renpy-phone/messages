# Screens shown while the phone is closed.

## Floating phone button with a badge. Added to config.overlay_screens when
## phone.cfg.hud is True. Hide it for a scene with phone.hide_hud().
screen phone_hud():
    zorder 50
    style_prefix "phone"

    if phone.hud_visible():
        button:
            style "phone_hud_button"
            xalign phone.cfg.hud_xalign
            yalign phone.cfg.hud_yalign
            action phone.Show()
            alt _("Open phone")

            add phone.circle("bezel", phone.px(72))
            text "☏" style "phone_glyph" size phone.px(34) color "#ffffff" align (0.5, 0.5)

            $ count = phone.total_badges()
            if count:
                use phone_badge(count, xalign=1.0, yalign=0.0)


transform phone_banner_in:
    on show:
        yoffset -phone.px(120)
        easein 0.25 yoffset 0
    on hide:
        easeout 0.2 yoffset -phone.px(120)


## Banner for phone.notify(). Tapping it opens the app it came from.
screen phone_notification(title, text="", app_id=None, icon=None):
    zorder 200
    style_prefix "phone"

    timer phone.cfg.notification_duration action Hide("phone_notification")

    button:
        style "phone_notification"
        at phone_banner_in
        action ([Hide("phone_notification"), phone.Show(app_id)] if app_id else Hide("phone_notification"))

        hbox:
            spacing phone.px(12)
            if icon is not None:
                add icon yalign 0.5
            elif app_id and phone.get_app(app_id):
                add phone.app_icon(phone.get_app(app_id), phone.px(44)) yalign 0.5
            vbox:
                yalign 0.5
                xsize phone.px(350)
                text title style "phone_row_title" substitute False
                if text:
                    text text style "phone_row_subtext" substitute False
