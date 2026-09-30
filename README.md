# Ren'Py Phone Framework

A drop-in smartphone for Ren'Py 8 games. It includes Messages (branching texts and group chats), a photo feed ("Photogram"), Phone calls, Settings and Wallpapers. You can also add your own apps.

- **Drop-in:** copy one folder, write a few lines of script.
- **Save and rollback safe:** story state lives in `default` variables and refers to contacts by id, so saves survive game updates.
- **Resolution independent:** sizes are authored at 1080p and scaled, so the phone looks the same at 720p, 1080p and 1440p/4K.
- **Themeable:** light and dark themes, player text size and 24-hour clock settings, restylable `phone_*` styles.
- **No art required:** icons, bubbles, avatars and wallpapers are drawn from a few white shapes tinted at runtime. Swap in your own images whenever you like.

Requires Ren'Py 8.1 or newer (it uses `_ren.py` files); tested on 8.5.3. The code stays Python 3.9 compatible.

## Install

1. Copy `game/phone/` into your game's `game/` folder, keeping the name `phone`.
2. Define contacts and use the API from your script. That's it.

The rest of this repository is a demo project and its test suite. Open the repository folder in the Ren'Py launcher to play the demo.

## Quick start

```renpy
define e = Character("Eileen")
define eileen = phone.Contact("eileen", character=e, number="555-0142", call_label="call_eileen")

label start:
    "My phone buzzes."
    $ phone.text(eileen, "Are you coming tonight?",
        phone.Reply("Yes!", then=phone.Chat().say("See you at 8!").set("going", True)),
        phone.Reply("Can't, sorry.", then=["Oh well."]))
    $ phone.open_chat(eileen)      # blocks until the player closes the phone

    $ phone.social.post(eileen, "eileen_selfie", "New haircut!", likes=120)
    $ phone.incoming_call(eileen, label="call_eileen")
    "After the call..."
    return

label call_eileen:
    e "Hi! Just checking you got my text."
    return
```

A floating phone button (with a badge for unread items) appears in the corner while the phone is closed. The player can open the phone from it at any time.

## Concepts

- **Everything is in the `phone` namespace** (a Ren'Py named store): `phone.Contact`, `phone.open`, `phone.cfg`...
- **Contacts are static.** Create them with `define`. What changes during the story (known, renamed, a different call label) is saved per playthrough by id. Never change a contact's id after release.
- **Chats are templates.** A `phone.Chat` can be `define`d once and sent many times. Building one touches no saved state; `send()` queues a copy.
- **Effects are Ren'Py actions.** Anything that runs later (replies, likes, comment options) takes actions such as `SetVariable`, `IncrementVariable`, `Function(module_level_function)` or `Jump`. They must pickle; in developer mode the framework raises right away if one doesn't.

## Opening and controlling the phone

| Call | What it does |
|---|---|
| `phone.open(app=None, screen=None, **kw)` | Shows the phone and waits until the player closes it. |
| `phone.show(...)` / `phone.close()` | Show without blocking / close. |
| `phone.Show(app)`, `phone.Toggle()`, `phone.Close()` | Screen actions, e.g. `key "K_p" action phone.Toggle()`. |
| `phone.Launch(app, screen=None, **kw)`, `phone.Navigate(screen, **kw)`, `phone.Back()`, `phone.Home()` | Navigation actions for app screens. |
| `phone.enable()` / `phone.disable()` | Allow or block opening the phone (for example during a cutscene). |
| `phone.show_hud()` / `phone.hide_hud()` | Show or hide the floating phone button. |
| `phone.set_time("21:34")` / `phone.set_battery(20)` | Story clock and battery in the status bar (`set_time(None)` = real time). |
| `phone.install_app(id)` / `phone.uninstall_app(id)` | Add or remove an app from the home screen for this playthrough. |
| `phone.notify(title, text, app_id=None)` | Show a banner (only while the phone is closed). |
| `phone.add_contact(c)`, `phone.rename_contact(c, name)`, `phone.set_avatar(c, img)`, `phone.set_call_label(c, label)` | Per-playthrough contact changes. |

`phone.Contact(id, name=None, avatar=None, character=None, number=None, handle=None, color=None, call_label=None, known=False)`: the name defaults to the Character's name and supports interpolation (`"[sister_name]"`). Without an avatar, a colored circle with the initial is drawn.

## Messages

```renpy
define date_chat = phone.Chat(eileen).note("Today").say("Dinner?").choice(
    phone.Reply("Sure!", effects=SetVariable("dinner", True), then=phone.Chat().say("8pm!")),
    phone.Reply("Busy.", then=["Another time then."]),
)
define crew = phone.group("crew", "Weekend crew", [lucy, max_])

label chapter2:
    $ date_chat.send()
    $ phone.Chat(crew).say("Look!", sender=lucy).image("beach photo", sender=lucy).send()
    $ phone.open_chat(eileen)
    while phone.waiting_for_reply(eileen):
        "I should answer her."
        $ phone.open_chat(eileen)
```

- **`Chat(who)` builder methods:**
  - `.say(text, sender=None)`: a message from the contact, or from `sender` in a group.
  - `.image(img, sender=None)`: an image message.
  - `.me(text)`: a message from the player.
  - `.note(text)`: a centered note such as a date.
  - `.choice(*replies)`: reply options for the player.
  - `.set(var, value)`, `.add(var, n)`, `.effect(action)`: run when playback reaches that point.
  - `.send()`: queues a copy of the chat.
- **`Reply(text, then=None, effects=None, image=None)`:** `then` is a Chat, or a list of Chats and plain strings. It plays after the player picks this reply.
- **Shortcuts:**
  - `phone.text(who, message, *replies)` and `phone.send_image(who, img)`.
  - `phone.open_chat(who)`.
  - `phone.waiting_for_reply(who)`, `phone.unread(who=None)`, `phone.chat_log(who)`, `phone.clear_chat(who)`, `phone.choose_reply(who, index)`.
- **Delivery:** while a conversation is open, messages arrive one by one with a typing indicator (`phone.cfg.messages_typing_delay`, default 0.8s; 0 disables it). Otherwise they arrive at once, count as unread and show a banner. Delivery stops at a message with choices until the player answers.

## Photogram (social feed)

```renpy
init python:
    phone.social_profile("lucy", bio="Illustrator.", followers=1284, following=312)

label beach:
    $ phone.social.post("lucy", "beach photo", "Sun and sand.", likes=214, time="1h",
        on_like=IncrementVariable("lucy_affection"),
        comments=[("max", "Jealous.")],
        comment_options=[phone.CommentOption("You look so happy!", IncrementVariable("lucy_affection"))])
    $ phone.open("social")
```

- **Posting and commenting** (`who=None` is the player):
  - `phone.social.post(who, image, caption="", likes=0, comments=(), comment_options=(), on_like=None, time=None, notify=True)` returns the post's uid.
  - `phone.social.comment(post_uid, who, text)`.
- **Likes and follows:** `like(uid)` / `unlike(uid)` / `liked(uid)`, and `follow(who)` / `unfollow(who)` / `following(who)`.
- **Lookups and edits:** `posts_by(who)`, `get(uid)`, `delete(uid)`, `set_likes`, `set_bio`, `set_followers`.
- **Player actions:**
  - Liking runs `on_like` the first time only.
  - Each preset comment option can be posted once.
  - Tapping a photo opens it full screen.
  - Tapping a name opens that person's profile.
- **Renaming the app:** `phone.social.name = "InstaPic"` in an init block.

## Phone calls

```renpy
label evening:
    $ phone.incoming_call(eileen, label="call_eileen", decline_label="ignored_eileen")
    $ phone.missed_call(max_)
    $ phone.start_call(lucy)        # a call written inline in the story
    l "Hey, got a minute?"
    $ phone.end_call()
```

- **Incoming calls:** `incoming_call(who, label=None, decline_label=None, can_decline=True, ring=True)` shows a ringing screen.
  - When the player accepts, `label` plays as a call, with an in-call pill on screen.
  - Without labels, it returns True or False.
- **Other calls:**
  - `start_call(who)` / `end_call()` / `in_call()`: a call written inline in the story.
  - `missed_call(who)`: logs a missed call and adds to the badge.
  - `log_call(who, direction)`: adds a log entry directly.
- **Placing calls from the app:** Recents, Contacts and Keypad tabs. Calling a contact plays its `call_label`, which you can change with `phone.set_call_label`. Contacts without one don't answer. `who` can also be a raw number for unknown callers.

## Settings and wallpapers

- **Settings are player preferences shared by all saves:**
  - dark mode (`phone.set_theme("dark")`)
  - text size (`phone.set_text_scale(1.2)`)
  - banners, sounds and the 24-hour clock
- **Adding your own toggles:** `phone.add_toggle_setting("Show hints", "show_hints", description=..., persistent=False, section="Game")`, or `phone.add_action_setting(label, action)`.
- **Wallpapers:**
  - `phone.add_wallpaper(id, image, name=None, locked=False)` at init. Six generated wallpapers are included; `phone.clear_wallpapers()` removes them.
  - `phone.unlock_wallpaper(id)` shows a banner and a badge. Also `phone.set_wallpaper(id)`, `phone.current_wallpaper()`.

## Configuration and theming

Change `phone.cfg` in an `init -2` block, so the values are in place before the phone's styles are built:

```renpy
init -2 python in phone:
    cfg.player_name = "Sam"
    cfg.zoom = 0.9                     # overall size tweak
    cfg.xalign = 0.8                   # put the phone right of center
    cfg.hud = False                    # no floating button
    cfg.themes["light"]["accent"] = "#e91e63"
    cfg.sounds["message"] = "audio/ping.ogg"
    cfg.default_wallpaper = "dusk"
```

`lint` warns if `cfg` sizes, fonts or theme colors are changed too late.

- **Styles:** every style is named `phone_*` and can be overridden with your own `style phone_...:` statements at the normal init level. Colors come from `cfg.themes` (keys like `bg`, `surface`, `text`, `accent`, `bubble_in`, `bubble_out`), so theme switching works.
- **Icons:** each app draws a `glyph` on a colored tile. Set `App.icon` to an image to use real artwork.

## Writing your own app

```renpy
init python in phone:
    class BankState(object):
        def __init__(self):
            self.balance = 0

    class BankApp(App):
        id = "bank"
        name = _("Bank")
        screen = "phone_bank"
        glyph = "✦"
        color = "#2e7d32"

        def reset(self):
            global bank_state
            bank_state = BankState()

    register_app(BankApp())

default phone.bank_state = phone.BankState()

screen phone_bank():
    use phone_page(_("Bank")):
        text "Balance: $[phone.bank_state.balance]" style "phone_title" align (0.5, 0.3)
```

- **Screen placement:** app screens are `use`d inside the phone, in a box of `phone.content_size()`.
- **Components:** build them from `phone_page`, `phone_list`, `phone_row`, `phone_tabs`, `phone_toggle`, `phone_badge`, `phone_empty` and `phone_image_viewer`.
- **Navigation and sizing:**
  - Navigate with `phone.Navigate(screen, **ids)`.
  - Size with `phone.px(n)` (1080p pixels).
  - Color with `phone.color(key)`.
- **App hooks:** implement `badge()` for the icon count and `on_launch(**kw)` for work to do on open.
- **State changes:** changes from screens should go through a `phone.PhoneAction` subclass (implement `run()`), so they survive saving mid-interaction.

## Project layout

```
game/phone/            the framework (copy this)
  core/                config, contacts, apps registry, state, actions, API
  screens/             phone shell, shared components, HUD, styles
  apps/<app>/          messages, social, calls, settings, wallpapers
  images/              white shapes tinted at runtime (tools/gen_assets.py)
game/demo/, script.rpy, options.rpy   demo project
game/tests/            in-engine tests
tools/test.sh          lint + tests at 720p, 1080p and 1440p
```

## Development

```sh
RENPY_SDK=/path/to/renpy-8.5.3-sdk tools/test.sh --shots /tmp/shots
```

This runs `renpy lint`, then starts the game headlessly under `xvfb-run` at three resolutions.

- **Tests:** every label named `test_*` in `game/tests/` runs as a test, and failures are reported.
- **Screenshots:** they go to `--shots`.
- **CI:** GitHub Actions runs the same script on every push.
