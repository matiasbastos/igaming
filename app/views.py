from flask import g, jsonify, render_template
from flask_login import login_required
from flask_appbuilder import ModelView, BaseView, expose
from flask_appbuilder.models.mongoengine.interface import MongoEngineInterface
from application import appbuilder
from models import Bonus, Wallet
from igamming_platform import Game


# Views
class WalletModelView(ModelView):
    datamodel = MongoEngineInterface(Wallet)
    list_columns = ['transaction_type', 'currency', 'value', 'bonus.name',
                    'user', 'bonus_cashed', 'timestamp']
    add_columns = ['transaction_type', 'currency', 'value', 'bonus',
                   'bonus_cashed', 'user']
    edit_columns = ['transaction_type', 'currency', 'value', 'bonus',
                    'bonus_cashed', 'user']


class BonusModelView(ModelView):
    datamodel = MongoEngineInterface(Bonus)
    list_columns = ['name', 'value', 'wagering_requirement', 'trigger']


# Game API
class GameView(BaseView):
    route_base = "/game"

    @login_required
    @expose('/deposit/<int:amount>')
    def deposit(self, amount):
        game = Game(str(g.user.id))
        return jsonify(game.deposit(amount))

    @login_required
    @expose('/play/<int:amount>')
    def play(self, amount):
        game = Game(str(g.user.id))
        return jsonify(game.play(amount))


# Global 404 handler
@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html',
                           base_template=appbuilder.base_template,
                           appbuilder=appbuilder), 404


# Admin menu
appbuilder.add_view(BonusModelView, "List Bonuses", icon="fa-trophy",
                    category="Gaming Platform", category_icon='fa-gamepad')
appbuilder.add_view(WalletModelView, "List Wallets", icon="fa-money",
                    category="Gaming Platform", category_icon='fa-gamepad')

# Expose endpoints
appbuilder.add_view_no_menu(GameView())

# Rebuild security model
appbuilder.security_cleanup()
