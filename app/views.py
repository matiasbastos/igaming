from flask import render_template
from flask_appbuilder import ModelView
from flask_appbuilder.models.mongoengine.interface import MongoEngineInterface
from app import appbuilder
from models import Bonus, Wallet


# Views
class WalletModelView(ModelView):
    datamodel = MongoEngineInterface(Wallet)
    list_columns = ['transaction_type', 'currency', 'value', 'bonus.name',
                    'user', 'bonus_cashed', 'created_on']
    add_columns = ['transaction_type', 'currency', 'value', 'bonus', 'user']
    edit_columns = ['transaction_type', 'currency', 'value', 'bonus', 'user']


class BonusModelView(ModelView):
    datamodel = MongoEngineInterface(Bonus)
    list_columns = ['name', 'value', 'wagering_requirement', 'trigger']


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

# Rebuild security model
appbuilder.security_cleanup()
