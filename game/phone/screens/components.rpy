# Building blocks for app screens. Custom apps should use these so they look
# and behave like the built-in ones.

## A page with a header and a body. Put the page content in the block:
##
##     use phone_page(_("Messages")):
##         viewport: ...
screen phone_page(title, back=True, right_text=None, right_action=None):
    vbox:
        use phone_header(title, back=back, right_text=right_text, right_action=right_action)
        frame:
            style "phone_body"
            transclude


screen phone_header(title, back=True, right_text=None, right_action=None):
    frame:
        style "phone_header"

        text title style "phone_header_title" xmaximum phone.px(300)

        if back:
            textbutton _("‹ Back"):
                style "phone_header_button"
                xalign 0.0
                action phone.Back()

        if right_text is not None:
            textbutton right_text:
                style "phone_header_button"
                xalign 1.0
                action right_action

    use phone_divider


## A scrolling list body. Items go in the block.
screen phone_list():
    viewport:
        scrollbars "vertical"
        mousewheel True
        draggable True
        pagekeys True
        yfill True

        vbox:
            xfill True
            transclude


## A tappable row: avatar, title, subtitle, and an optional badge or note.
screen phone_row(title, subtitle=None, who=False, badge=0, note=None, action=None, image=None):
    button:
        style "phone_row"
        action action

        hbox:
            spacing phone.px(14)
            xfill True

            if who is not False:
                add phone.avatar(who, phone.px(52)) yalign 0.5
            elif image is not None:
                add image yalign 0.5

            vbox:
                yalign 0.5
                xsize phone.px(250 if (badge or note) else 330)
                text title style "phone_row_title" substitute False
                if subtitle:
                    text subtitle style "phone_row_subtext" substitute False

            if badge or note:
                vbox:
                    xalign 1.0
                    yalign 0.5
                    spacing phone.px(4)
                    if note:
                        text note style "phone_subtext" size phone.text_px(15) xalign 1.0 substitute False
                    if badge:
                        use phone_badge(badge, xalign=1.0)

    use phone_divider


screen phone_divider():
    add Solid(phone.color("divider"), xsize=phone.content_size()[0], ysize=max(1, phone.px(1)))


screen phone_badge(count, **properties):
    frame:
        style "phone_badge"
        properties properties
        text ("99+" if count > 99 else str(count)) style "phone_badge_text"


## An on/off switch row, e.g. in Settings.
screen phone_toggle(label, value, action, description=None):
    button:
        style "phone_row"
        action action
        selected value

        hbox:
            xfill True
            vbox:
                yalign 0.5
                xsize phone.px(300)
                text label style "phone_row_title"
                if description:
                    text description style "phone_row_subtext"

            fixed:
                xalign 1.0
                yalign 0.5
                xysize (phone.px(52), phone.px(30))
                add phone.rounded("success" if value else "divider", "md")
                add phone.circle("#ffffff", phone.px(26)):
                    yalign 0.5
                    xpos (phone.px(24) if value else phone.px(2))

    use phone_divider


## A row of tabs. tabs is a list of (label, action, selected).
screen phone_tabs(tabs):
    frame:
        background phone.color("surface")
        xfill True
        padding (0, 0)
        hbox:
            xfill True
            for label, action, is_selected in tabs:
                textbutton label:
                    style "phone_tab"
                    xsize (phone.content_size()[0] // max(1, len(tabs)))
                    action action
                    selected is_selected
    use phone_divider


## Centered placeholder text for empty lists.
screen phone_empty(message):
    fixed:
        text message style "phone_empty_text"


## Full-screen image viewer; open it with phone.Navigate("phone_image_viewer", image=...).
screen phone_image_viewer(image):
    add Solid("#000")
    button:
        style "empty"
        xfill True
        yfill True
        action phone.Back()
        alt _("Close image")
        add Transform(image, fit="contain", xysize=phone.content_size()) align (0.5, 0.5)
