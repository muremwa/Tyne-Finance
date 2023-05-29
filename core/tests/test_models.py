from django.test import TestCase
from django.db import IntegrityError

from core.models import Currency, User, AccountType, Account


class CoreModelsTestCase(TestCase):

    def setUp(self) -> None:
        self.currency = Currency.objects.create(country='Kenya', code='KES', symbol='Ksh')
        self.user = User.objects.create(
            username='tyne',
            email='tyne@tfinance.io',
            currency=self.currency
        )

    def test_currency(self):
        self.assertEquals(self.currency.code, 'KES')
        self.assertRaises(
            IntegrityError,
            lambda kgs: Currency.objects.create(**kgs),
            {'country': 'Kenya', 'code': 'KES', 'symbol': 'Ksh'}
        )

    def test_user(self):
        self.assertEquals(self.user.currency.code, 'KES')

    def test_accounts(self):
        account_type = AccountType.objects.create(name='Mobile Money', code='MNO')
        account = Account.objects.create(
            account_type=account_type,
            user=self.user,
            account_number='01',
            account_provider='SAF',
        )
        self.assertEquals(account.account_type.code, 'MNO')
        self.assertEquals(account.account_number, '01')
        self.assertIsNotNone(account.date_added)
        self.assertIsNotNone(account.date_modified)
        self.assertIsNone(account.last_balance_update)
        self.assertEquals(account.balance, 0)
        self.assertFalse(account.active)

