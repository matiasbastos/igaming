from random import random
from models import TRANSACTION, CURRENCY, Wallet, Bonus


class Game:
    """
    Game helper functions
    """
    def wins():
        """
        Simulates a spin.
        return: random true/false
        """
        return random() < 0.5  # 50/50

    def add_to_wallet(self, data):
        """
        Encapsulates the saving into the wallet
        return: wallet saved row
        """
        rec = Wallet(**data)
        rec.save()
        return rec

    def count_wagered_money():
        pass

    def get_bonus_to_cash():
        pass

    def cash_in():
        pass

    def get_bonus_money():
        pass

    def get_real_money():
        pass

    """
    Bonus Triggers
    """
    def on_deposit():
        pass

    def on_login():
        pass


    """
    Player actions
    """
    def deposit(self, user, amount):
        self.add_to_wallet({'transaction_type':'DEPOSIT',
                            'currency': 'BNS',
                            'value': amount,
                            'user': user})
        self.on_deposit()

    def play():
        pass
