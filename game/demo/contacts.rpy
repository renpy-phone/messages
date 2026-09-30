## Demo cast, shared by every app demo. Contacts are static: define them.

define e = Character("Eileen", color="#c8ffc8")
define l = Character("Lucy", color="#ffc8e0")
define m = Character("Max", color="#c8e0ff")

define eileen = phone.Contact("eileen", character=e, number="555-0142", handle="eileen.codes", known=True)
define lucy = phone.Contact("lucy", character=l, number="555-0199", handle="lucy_draws")
define max_ = phone.Contact("max", character=m, number="555-0107", handle="maxmoves")

# Placeholder "photos" so the demo needs no image files.
image demo photo beach = Fixed(Solid("#4fc3f7"), Solid("#ffe082", ysize=0.35, yalign=1.0), Transform("phone/images/circle.png", xysize=(160, 160), matrixcolor=TintMatrix("#fff59d"), xalign=0.8, yalign=0.2), xysize=(1080, 1080))
image demo photo city = Fixed(Solid("#263238"), Solid("#546e7a", xsize=0.2, ysize=0.6, xalign=0.1, yalign=1.0), Solid("#78909c", xsize=0.25, ysize=0.8, xalign=0.5, yalign=1.0), Solid("#455a64", xsize=0.2, ysize=0.5, xalign=0.9, yalign=1.0), xysize=(1080, 1080))
image demo photo cat = Fixed(Solid("#ffccbc"), Transform("phone/images/circle.png", xysize=(600, 600), matrixcolor=TintMatrix("#ff8a65"), align=(0.5, 0.7)), xysize=(1080, 1350))
