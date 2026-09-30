## Demo cast, shared by every app demo. Contacts are static: define them.

define e = Character("Eileen", color="#c8ffc8")
define l = Character("Lucy", color="#ffc8e0")
define m = Character("Max", color="#c8e0ff")

define eileen = phone.Contact("eileen", character=e, number="555-0142", handle="eileen.codes", known=True)
define lucy = phone.Contact("lucy", character=l, number="555-0199", handle="lucy_draws")
define max_ = phone.Contact("max", character=m, number="555-0107", handle="maxmoves")

# Demo pictures (rendered by tools/art/demo_art.rpy).
image demo photo beach = "images/demo/beach.png"
image demo photo city = "images/demo/city.png"
image demo photo cat = "images/demo/cat.png"
