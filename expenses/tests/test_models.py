from django.test import TestCase
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from core.models import User, Account, Currency, AccountType
from expenses.models import UsageTag, Expense, RecurringPayment


class ExpenseModelsTestCase(TestCase):

    def setUp(self) -> None:
        self.currency = Currency.objects.create(country='Kenya', code='KES', symbol='Ksh')
        self.user = User.objects.create(
            username='tyne',
            email='tyne@tfinance.io',
            currency=self.currency
        )
        self.usage_tag = UsageTag.objects.create(title='Wash', code='WH')
        self.usage_tag_2 = UsageTag.objects.create(title='FOOD', code='FD')
        self.account_type = AccountType.objects.create(name='Mobile Money', code='MNO')
        self.account = Account.objects.create(
            account_type=self.account_type,
            user=self.user,
            account_number='01',
            account_provider='SAF',
        )

    def test_usage_tag(self):
        self.assertRaises(
            IntegrityError,
            lambda kgs: UsageTag.objects.create(**kgs),
            {'title': 'Wear', 'code': 'WH'}
        )

    def test_expense(self):
        expense = Expense.objects.create(
            account=self.account,
            date_occurred='2022-03-02'
        )
        expense.tags.add(self.usage_tag, self.usage_tag_2)
        self.assertFalse(expense.planned)
        self.assertTrue(all([num == 0 for num in [expense.transaction_charge, expense.amount]]))
        self.assertIsNotNone(expense.date_created)
        self.assertListEqual(
            [tag.code for tag in expense.tags.all()],
            [self.usage_tag.code, self.usage_tag_2.code]
        )

    def test_recurring_payments(self):
        payment = RecurringPayment.objects.create(
            account=self.account,
            start_date='2022-03-02',
            renewal_date='12-31'
        )
        payment.tags.add(self.usage_tag, self.usage_tag_2)
        self.assertTrue(all([num == 0 for num in [payment.transaction_charge, payment.amount]]))
        self.assertIsNotNone(payment.date_added)
        self.assertIsNotNone(payment.date_modified)
        self.assertIs(payment.renewal_count, 0)
        self.assertTrue(payment.is_annual)
        self.assertListEqual(
            [tag.code for tag in payment.tags.all()],
            [self.usage_tag.code, self.usage_tag_2.code]
        )
        payment.renewal_date = '8'
        payment.save()
        self.assertFalse(payment.is_annual)
