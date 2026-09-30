## Keeps the README's custom app example honest.

init python in phone:
    class BankState(object):
        def __init__(self):
            self.balance = 0

    class BankApp(App):
        id = "bank"
        name = _("Bank")
        screen = "phone_bank"
        icon = Solid("#2e7d32")  # a real game ships gui/phone/apps/bank/icon_idle.png

        def reset(self):
            global bank_state
            bank_state = BankState()

    register_app(BankApp())

default phone.bank_state = phone.BankState()

screen phone_bank():
    use phone_page(_("Bank")):
        text "Balance: $[phone.bank_state.balance]" style "phone_title" align (0.5, 0.3)

label test_readme_custom_app:
    $ phone.bank_state.balance = 42
    $ phone.show("bank")
    $ expect_eq(phone.state.current()[0], "phone_bank", "custom app launches")
    $ shot("readme-bank")
    $ phone.close()
    $ phone.reset_apps()
    $ expect_eq(phone.bank_state.balance, 0, "reset() restores the app state")
    return
