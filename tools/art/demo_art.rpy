## Pictures used by the demo story (game/images/demo/). Not part of the
## framework.

init -90 python in phone_art:

    file_spec("images/demo/beach.png", (1080, 1080), lambda: layers(
        1080, 1080,
        Solid("#4fc3f7"),
        Solid("#ffe082", ysize=0.35, yalign=1.0),
        Transform(circle("#fff59d", 160), xalign=0.8, yalign=0.2),
    ))

    file_spec("images/demo/city.png", (1080, 1080), lambda: layers(
        1080, 1080,
        Solid("#263238"),
        Solid("#546e7a", xsize=0.2, ysize=0.6, xalign=0.1, yalign=1.0),
        Solid("#78909c", xsize=0.25, ysize=0.8, xalign=0.5, yalign=1.0),
        Solid("#455a64", xsize=0.2, ysize=0.5, xalign=0.9, yalign=1.0),
    ))

    file_spec("images/demo/cat.png", (1080, 1350), lambda: layers(
        1080, 1350,
        Solid("#ffccbc"),
        Transform(circle("#ff8a65", 600), align=(0.5, 0.7)),
    ))
