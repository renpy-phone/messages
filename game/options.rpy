## Demo project settings. Only game/phone/ is part of the framework; this file
## and the rest of game/ exist to show it off and to test it.

init -2 python:
    import os

    # The test runner sets PHONE_TEST_RES to check other resolutions.
    _phone_demo_res = os.environ.get("PHONE_TEST_RES", "1920x1080").split("x")
    gui.init(int(_phone_demo_res[0]), int(_phone_demo_res[1]))

define config.name = "Phone Framework Demo"
define config.version = "1.0"
define config.save_directory = "phone-framework-demo"
define config.window_title = config.name
define config.check_conflicting_properties = True
define build.name = "PhoneFrameworkDemo"
