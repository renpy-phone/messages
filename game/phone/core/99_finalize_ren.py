"""renpy
init 900 python in phone:
"""

# Runs after the game's own init code, so it sees the final configuration.

if cfg.hud and "phone_hud" not in store.config.overlay_screens:
    store.config.overlay_screens.append("phone_hud")

if _after_load not in store.config.after_load_callbacks:
    store.config.after_load_callbacks.append(_after_load)


def _lint():
    if _style_inputs() != _style_snapshot:
        print(
            "phone: phone.cfg size, font or theme settings were changed after the "
            "phone styles were built (init -1). Change them in an "
            "`init -2 python in phone:` block instead."
        )
    for app in apps.values():
        if not app.screen or not renpy.has_screen(app.screen):
            print("phone: app {!r} uses screen {!r}, which does not exist.".format(app.id, app.screen))
    for key in ("light", "dark"):
        if key not in cfg.themes:
            print("phone: cfg.themes has no {!r} theme.".format(key))
    if cfg.default_theme not in cfg.themes:
        print("phone: cfg.default_theme {!r} is not in cfg.themes.".format(cfg.default_theme))
    ids = [w[0] for w in cfg.wallpapers]
    if len(ids) != len(set(ids)):
        print("phone: cfg.wallpapers has duplicate ids.")
    for c in contacts.values():
        if c.call_label and not renpy.has_label(c.call_label):
            print("phone: contact {!r} has call_label {!r}, which does not exist.".format(c.id, c.call_label))


if _lint not in store.config.lint_hooks:
    store.config.lint_hooks.append(_lint)
