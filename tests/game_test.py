from tests import create_app, create_user, drop_db
from mock import MagicMock
from app.igamming_platform import Game, Wallet, Bonus


class TestGame:
    app = None
    db = None
    user = None
    game = None

    def setup_class(self):
        self.app, self.db = create_app()
        self.user = create_user(self.app)

    def teardown_class(self):
        drop_db()

    def setup_method(self, method):
        self.game = Game(str(self.user.id))

    def teardown_method(self, method):
        Wallet.drop_collection()
        Bonus.drop_collection()

    def test_user(self):
        assert self.user.username == 'test_user'

    def test_add_to_wallet(self):
        self.game.add_to_wallet({'transaction_type': 'DEPOSIT',
                                 'currency': 'EUR',
                                 'value': 3456,
                                 'user': self.user})
        w = Wallet.objects[0]
        assert w.value == 3456

    def test_count_wagered_money(self):
        # no bets so should be 0
        assert self.game.count_wagered_money() == 0
        # deposit some money
        self.game.add_to_wallet({'transaction_type': 'DEPOSIT',
                                 'currency': 'EUR',
                                 'value': 3456,
                                 'user': self.user})
        assert self.game.count_wagered_money() == 0
        # start playing
        self.game.add_to_wallet({'transaction_type': 'BET',
                                 'currency': 'EUR',
                                 'value': 3456,
                                 'user': self.user})
        assert self.game.count_wagered_money() == 3456
        # create bonus
        test_bonus = Bonus(name='test_bonus',
                           value=100,
                           wagering_requirement=10,
                           trigger='on_login').save()
        assert len(Bonus.objects()) == 1
        # cashin a bonus that need 1000 EUR spent on spins
        self.game.add_to_wallet({'transaction_type': 'CASHIN',
                                 'currency': 'EUR',
                                 'value': 100,
                                 'bonus': test_bonus,
                                 'user': self.user})
        assert self.game.count_wagered_money() == 2456

    def test_get_already_cashed_bonuses(self):
        # no cashins so should be len 0
        assert self.game.get_already_cashed_bonuses() == []
        # create bonus
        test_bonus = Bonus(name='test_bonus',
                           value=100,
                           wagering_requirement=10,
                           trigger='on_login').save()
        assert len(Bonus.objects()) == 1
        # add bonus
        bonus = self.game.add_to_wallet({'transaction_type': 'BONUS',
                                         'currency': 'BNS',
                                         'value': test_bonus.value,
                                         'bonus': test_bonus.id,
                                         'user': self.user})
        assert len(Wallet.objects()) == 1
        # cashin a bonus that need 1000 EUR spent on spins
        self.game.add_to_wallet({'transaction_type': 'CASHIN',
                                 'currency': 'EUR',
                                 'value': 456,
                                 'bonus': test_bonus,
                                 'bonus_cashed': bonus,
                                 'user': self.user})
        assert len(self.game.get_already_cashed_bonuses()) == 1

    def test_get_bonus_money(self):
        # no bonuses so should be 0
        assert self.game.get_bonus_money() == 0
        # create bonus
        test_bonus = Bonus(name='test_bonus',
                           value=100,
                           wagering_requirement=10,
                           trigger='on_login').save()
        assert len(Bonus.objects()) == 1
        # add bonus
        self.game.add_to_wallet({'transaction_type': 'BONUS',
                                 'currency': 'BNS',
                                 'value': test_bonus.value,
                                 'bonus': test_bonus.id,
                                 'user': self.user})
        assert len(Wallet.objects()) == 1
        # expected to have 100 bonus
        assert self.game.get_bonus_money() == 100

    def test_get_real_money(self):
        # no money so should be 0
        assert self.game.get_real_money() == 0
        # deposit 3456
        self.game.add_to_wallet({'transaction_type': 'DEPOSIT',
                                 'currency': 'EUR',
                                 'value': 3456,
                                 'user': self.user})
        assert self.game.get_real_money() == 3456
        # lost 3456
        self.game.add_to_wallet({'transaction_type': 'BET',
                                 'currency': 'EUR',
                                 'value': -3456,
                                 'user': self.user})
        assert self.game.get_real_money() == 0

    def test_cashin(self):
        # lets try but nothing should happen
        self.game.cash_in()
        filter_by = {'user': self.user,
                     'transaction_type': 'CASHIN'}
        assert len(Wallet.objects(**filter_by)) == 0
        # create bonus
        test_bonus = Bonus(name='test_bonus',
                           value=100,
                           wagering_requirement=10,
                           trigger='on_login').save()
        assert len(Bonus.objects()) == 1
        # add bonus
        self.game.add_to_wallet({'transaction_type': 'BONUS',
                                 'currency': 'BNS',
                                 'value': test_bonus.value,
                                 'bonus': test_bonus.id,
                                 'user': self.user})
        assert len(Wallet.objects()) == 1
        # deposit 1000 EUR
        self.game.add_to_wallet({'transaction_type': 'DEPOSIT',
                                 'currency': 'EUR',
                                 'value': 1000,
                                 'user': self.user})
        assert self.game.get_real_money() == 1000
        # lost 1000 EUR
        self.game.add_to_wallet({'transaction_type': 'BET',
                                 'currency': 'EUR',
                                 'value': -1000,
                                 'user': self.user})
        assert self.game.get_real_money() == 0
        # 100 EUR should be cashed
        self.game.cash_in()
        assert self.game.get_real_money() == 100
        filter_by = {'user': self.user,
                     'transaction_type': 'CASHIN'}
        assert len(Wallet.objects(**filter_by)) == 1
        # lost 100 EUR
        self.game.add_to_wallet({'transaction_type': 'BET',
                                 'currency': 'EUR',
                                 'value': -100,
                                 'user': self.user})
        assert self.game.get_real_money() == 0
        # add new bonus
        self.game.add_to_wallet({'transaction_type': 'BONUS',
                                 'currency': 'BNS',
                                 'value': test_bonus.value,
                                 'bonus': test_bonus.id,
                                 'user': self.user})
        assert self.game.get_bonus_money() == 100
        # lost 50 BNS
        self.game.add_to_wallet({'transaction_type': 'BET',
                                 'currency': 'BNS',
                                 'value': -50,
                                 'user': self.user})
        assert self.game.get_bonus_money() == 50
        # deposit 1000 EUR
        self.game.add_to_wallet({'transaction_type': 'DEPOSIT',
                                 'currency': 'EUR',
                                 'value': 1000,
                                 'user': self.user})
        assert self.game.get_real_money() == 1000
        # lost 1000 EUR
        self.game.add_to_wallet({'transaction_type': 'BET',
                                 'currency': 'EUR',
                                 'value': -1000,
                                 'user': self.user})
        assert self.game.get_real_money() == 0
        # 50 EUR should be cashed
        self.game.cash_in()
        assert self.game.get_real_money() == 50
        filter_by = {'user': self.user,
                     'transaction_type': 'CASHIN'}
        assert len(Wallet.objects(**filter_by)) == 3

    def test_events(self):
        # create bonus
        Bonus(name='test_bonus',
              value=100,
              wagering_requirement=10,
              trigger='on_login').save()
        assert len(Bonus.objects()) == 1
        assert self.game.get_bonus_money() == 0
        # no bonus should be asigned
        self.game.on_event('on_deposit')
        assert self.game.get_bonus_money() == 0
        # 100 BNS
        self.game.on_event('on_login')
        assert self.game.get_bonus_money() == 100

    def test_deposit(self):
        # make a deposit
        self.game.deposit(4321)
        assert Wallet.objects[0].value == 4321
        # create bonus
        Bonus(name='test_bonus',
              value=100,
              wagering_requirement=10,
              trigger='on_deposit').save()
        # the bonus should be asigned
        self.game.deposit(4321)
        assert Wallet.objects(currency='BNS').first().value == 100

    def test_play(self):
        # create bonus
        Bonus(name='test_bonus',
              value=100,
              wagering_requirement=10,
              trigger='on_deposit').save()
        Bonus(name='test_bonus 2',
              value=100,
              wagering_requirement=10,
              trigger='on_login').save()
        # play with out money
        play = self.game.play(100)
        assert play['status'] == 'warning'
        # make a deposit
        self.game.deposit(1000)
        assert self.game.get_real_money() == 1000
        assert self.game.get_bonus_money() == 100
        # win
        self.game.wins = MagicMock(return_value=True)
        play = self.game.play(500)
        assert play['status'] == 'ok'
        assert play['total_eur'] == 1500
        assert play['total_bns'] == 100
        # lost
        self.game.wins = MagicMock(return_value=False)
        play = self.game.play(1500)
        assert play['status'] == 'ok'
        assert play['total_eur'] == 100
        assert play['total_bns'] == 0
        play = self.game.play(100)
        assert play['status'] == 'ok'
        assert play['total_eur'] == 0
        assert play['total_bns'] == 0
        # add login bonus
        self.game.on_event('on_login')
        # now should play with bns
        self.game.wins = MagicMock(return_value=True)
        play = self.game.play(100)
        assert play['status'] == 'ok'
        assert play['total_eur'] == 0
        assert play['total_bns'] == 200
