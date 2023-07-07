from django.test import TestCase
from django.db import IntegrityError
from django.core.exceptions import PermissionDenied

from core.models import User, Account, Currency, AccountType
from expenses.models import UsageTag, Expense, RecurringPayment, Transaction


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
        self.expense = Expense.objects.create(
            account=self.account,
            date_occurred='2022-03-02'
        )
        self.payment = RecurringPayment.objects.create(
            user=self.user,
            start_date='2022-03-02',
            renewal_date='12-31'
        )

    def test_usage_tag(self):
        self.assertRaises(
            IntegrityError,
            lambda kgs: UsageTag.objects.create(**kgs),
            {'title': 'Wear', 'code': 'WH'}
        )

    def test_expense(self):
        self.expense.tags.add(self.usage_tag, self.usage_tag_2)
        self.assertFalse(self.expense.planned)
        self.assertTrue(all([num == 0 for num in [self.expense.transaction_charge, self.expense.amount]]))
        self.assertIsNotNone(self.expense.date_created)
        self.assertListEqual(
            [tag.code for tag in self.expense.tags.all()],
            [self.usage_tag.code, self.usage_tag_2.code]
        )

    def test_recurring_payments(self):
        self.payment.tags.add(self.usage_tag, self.usage_tag_2)
        self.assertTrue(all([num == 0 for num in [self.payment.transaction_charge, self.payment.amount]]))
        self.assertIsNotNone(self.payment.date_added)
        self.assertIsNotNone(self.payment.date_modified)
        self.assertIs(self.payment.renewal_count, 0)
        self.assertTrue(self.payment.is_annual)
        self.assertListEqual(
            [tag.code for tag in self.payment.tags.all()],
            [self.usage_tag.code, self.usage_tag_2.code]
        )
        self.payment.renewal_date = '8'
        self.payment.save()
        self.assertFalse(self.payment.is_annual)

    def test_transaction(self):
        transaction = Transaction.objects.create(
            transaction_type='DB',
            transaction_for='EX',
            transaction_for_id=self.expense.pk,
            amount=400,
            account=self.account
        )
        self.assertIsNotNone(transaction.pk)
        self.assertEquals(transaction.get_transaction_item(), self.expense)
        self.assertRaises(PermissionDenied, transaction.save)
        self.assertEquals(self.account.balance, 0 - 400)
        transaction.delete()
        self.assertEquals(self.account.balance, 0)
