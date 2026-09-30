## Demo scene for the Social app.

init python:
    phone.social_profile("lucy", bio="Illustrator. Coffee, sketchbooks and too many beach days.", followers=1284, following=312)
    phone.social_profile("max", bio="Running, rooftops and bad puns.", followers=530, following=498, followed=True)
    phone.social_profile("eileen", bio="Visual novels and tea.", followers=2210, following=150)
    phone.social_profile(None, bio="Just here for the cat pictures.", followers=87, following=40)

default lucy_affection = 0

label demo_social:
    e "Did you see? Lucy finally went to the beach."

    $ phone.social.post(None, "demo photo cat", "Meet the real boss of the house.", likes=23, time="Yesterday",
        comments=[("lucy", "THE BOSS!!"), ("max", "Those eyes...")])

    $ phone.social.post("max", "demo photo city", "City lights never get old.", likes=87, time="5h",
        comments=[("eileen", "Where is this?"), ("max", "Rooftop downtown. Best view in town.")])

    $ phone.social.post("lucy", "demo photo beach", "Sun, sand and zero deadlines. Back to the sketchbook tomorrow, promise.",
        likes=214, time="1h",
        on_like=IncrementVariable("lucy_affection"),
        comments=[("max", "Jealous."), ("eileen", "Look at those colors!")],
        comment_options=[
            phone.CommentOption("You look so happy here!", IncrementVariable("lucy_affection")),
            phone.CommentOption("Don't forget the sunscreen."),
        ])

    l "Posted it! Go on, tell me what you think."

    $ phone.open("social")

    if lucy_affection >= 2:
        l "A like AND a sweet comment? You're making me blush."
    elif lucy_affection == 1:
        l "Thanks for the like!"
    else:
        l "Hey, you didn't even like it..."

    return
