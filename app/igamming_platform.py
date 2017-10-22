"""
Simple IGaming Platform
"""
import logging
from random import random
from mongoengine import Document
from models import Wallet, Bonus, User


class Game(object):
    """
    IGaming Main Class
    """
    # Config logging
    log = None
    # current user object property
    user = None

    # class init
    def __init__(self, user):
        logging.basicConfig(format='%(asctime)s:%(levelname)s: %(message)s')
        self.log = logging.getLogger()
        self.log.setLevel(logging.INFO)
        if isinstance(user, str):
            user = User.objects(pk=user).first()
        if not isinstance(user, Document):
            raise Exception('The user parameter is not a mongoengine.Document')
        self.log.info('User: %s', user)
        self.user = user

    """
    Game helper functions
    """
    def wins(self):
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
        self.log.info('Added to wallet: %s', rec)
        return rec

    def count_wagered_money(self):
        """
        Sum of the total wagered money since the last cash-in
        return: wagered money
        """

        # get total wagered money
        filter_by = {'user': self.user,
                     'currency': 'EUR',
                     'transaction_type': 'BET'}
        bets = Wallet.objects(**filter_by).only('value')
        bets = sum([abs(b.value) for b in bets])

        # get total cashed in bonus requirements
        filter_by = {'user': self.user,
                     'transaction_type': 'CASHIN',
                     'value__gt': 0}
        cashins = Wallet.objects(**filter_by)
        cashins = sum([c.bonus.value * c.bonus.wagering_requirement
                       for c in cashins])

        return bets - cashins

    def get_already_cashed_bonuses(self):
        """
        Get already cashed bonuses
        return: cashed bonuses list
        """
        filter_by = {'user': self.user,
                     'transaction_type': 'CASHIN'}
        return [c.bonus_cashed.id for c in Wallet.objects(**filter_by)]

    def get_bonus_money(self):
        """
        Gets the total bonus money in the wallet
        return: bonus money amount
        """
        filter_by = {'user': self.user,
                     'currency': 'BNS',
                     'id__nin': self.get_already_cashed_bonuses()}
        return Wallet.objects(**filter_by).sum('value')

    def get_real_money(self):
        """
        Gets the total bonus money in the wallet
        return: bonus money amount
        """
        return Wallet.objects(user=self.user, currency='EUR').sum('value')

    def cash_in(self):
        """
        Convert to real money the bonuses that met the wagering req.
        """
        # get casheable bonuses
        filter_by = {'user': self.user,
                     'transaction_type': 'BONUS',
                     'id__nin': self.get_already_cashed_bonuses()}
        bonus = Wallet.objects(**filter_by).first()
        if bonus:
            # get wagered money
            wg = self.count_wagered_money()
            # WR formula is met?
            if bonus.bonus.value * bonus.bonus.wagering_requirement <= wg:
                # how much money from that bonus is going to be cashed?
                bns = self.get_bonus_money()
                # for the case that te player earned more bns than the bonus
                cashin_amount = bns if bns <= bonus.bonus else bonus.bonus.value
                transaction = {'transaction_type': 'CASHIN',
                               'currency': 'EUR',
                               'value': cashin_amount,
                               'bonus': bonus.bonus,
                               'bonus_cashed': bonus.id,
                               'user': self.user}
                # save cashin transaction
                self.add_to_wallet(transaction)
                # adjust bns diff if there is one (this need to be improved)
                if cashin_amount < bonus.bonus.value:
                    transaction = {'transaction_type': 'CASHIN',
                                   'currency': 'BNS',
                                   'value': bonus.bonus.value - cashin_amount,
                                   'bonus': bonus.bonus,
                                   'bonus_cashed': bonus.id,
                                   'user': self.user}
                    # save cashin transaction
                    self.add_to_wallet(transaction)
                # check if there is an other casheable bonus
                self.cash_in()

    """
    Bonus Triggers
    """
    def on_event(self, event):
        """
        Triggered when the player deposits money
        """
        self.log.info('Event Triggered: %s', event)
        # get bonuses
        bonuses = Bonus.objects(trigger=event)
        for bonus in bonuses:
            # add bonus
            self.add_to_wallet({'transaction_type': 'BONUS',
                                'currency': 'BNS',
                                'value': bonus.value,
                                'bonus': bonus.id,
                                'user': self.user})

    """
    Player actions
    """
    def deposit(self, amount):
        """
        Adds money to the real money wallet
        """
        try:
            # add money
            self.add_to_wallet({'transaction_type': 'DEPOSIT',
                                'currency': 'EUR',
                                'value': amount,
                                'user': self.user})
            # trigger
            self.on_event('on_deposit')

            return {'status': 'ok',
                    'amount': amount,
                    'total_eur': self.get_real_money(),
                    'total_bns': self.get_bonus_money()}
        except Exception as ex:
            self.log.error('Deposit Exception: %s', ex)
            return {'status': 'error',
                    'msg': 'Internal Server Error'}

    def play(self, amount):
        """
        Play a round
        """
        try:
            # get available money
            eur = self.get_real_money()
            if eur:
                currency = 'EUR'
                if eur < amount:
                    msg = 'Not enough EUR! Max bet: %s' % eur
                    return {'status': 'warning', 'msg': msg}
            else:
                currency = 'BNS'
                bns = self.get_bonus_money()
                if bns < amount:
                    msg = 'Not enough BNS! Max bet: %s' % bns
                    return {'status': 'warning', 'msg': msg}

            # get round result
            if not self.wins():
                amount = amount * -1
            self.log.info('You WON!!!' if amount > 0 else 'HA HA Loooooser!')

            # make transaction
            self.add_to_wallet({'transaction_type': 'BET',
                                'currency': currency,
                                'value': amount,
                                'user': self.user})

            # check for casheable bonuses
            if currency == 'EUR':
                self.cash_in()
            return {'status': 'ok',
                    'result': 'win' if amount > 0 else 'lost',
                    'amount': amount,
                    'total_eur': self.get_real_money(),
                    'total_bns': self.get_bonus_money()}
        except Exception as ex:
            self.log.error('Play Exception: %s', ex)
            return {'status': 'error',
                    'msg': 'Internal Server Error'}
