import time
from flask_appbuilder.security.mongoengine.models import User
from mongoengine import Document
from mongoengine import LongField, StringField, ReferenceField, IntField

TRIGGER = (('on_login', 'On Login'),
           ('on_deposit', 'On Deposit > 100 Euros'))
CURRENCY = (('EUR', 'Euro'),
            ('BNS', 'Bonus'))
TRANSACTION = (('BONUS', 'Bonus Award'),
               ('BET', 'Bet'),
               ('CASHIN', 'Cash-in'),
               ('DEPOSIT', 'Euro Deposit'))


class Bonus(Document):
    name = StringField(max_length=60, required=True, unique=True)
    value = IntField(required=True)
    wagering_requirement = IntField(required=True, min_value=1, max_value=100)
    trigger = StringField(required=True, max_length=60, choices=TRIGGER)

    meta = {
        'indexes': [
            'trigger',
        ]
    }

    def __unicode__(self):
        return "%s (%sEUR WR:%s %s)" % (self.name,
                                        self.value,
                                        self.wagering_requirement,
                                        self.trigger)


class Wallet(Document):
    transaction_type = StringField(required=True,
                                   max_length=10,
                                   choices=TRANSACTION)
    currency = StringField(required=True, max_length=3, choices=CURRENCY)
    value = IntField(required=True)
    bonus = ReferenceField(Bonus, required=False)
    bonus_cashed = ReferenceField('self')
    user = ReferenceField(User, required=True)
    timestamp = LongField(default=lambda: int(round(time.time() * 1000)))

    meta = {
        'indexes': [
            'user',
            'currency',
            'timestamp',
            'bonus_cashed',
        ],
        'ordering': ['-timestamp']
    }

    def __unicode__(self):
        return "%s %s %s %s %s" % (self.timestamp,
                                   self.user.username,
                                   self.transaction_type,
                                   self.value,
                                   self.bonus)
