from tests import create_app, create_user, drop_db
from app.igamming_platform import Game, Wallet, Bonus


class TestGame:
    app = None
    db = None
    user = None
    game = None

    def setup(self):
        self.app, self.db = create_app()
        self.user = create_user(self.app)
        print self.user

    def teardown(self):
        drop_db()

    def setup_method(self, method):
        self.game = Game(str(self.user.id))
        pass

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
