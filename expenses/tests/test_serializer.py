from django.test import TestCase

from core.models import Currency, User, Account, AccountType
from core.serializers import AccountTypeSerializer, UserSerializer
from core.utils import DateTimeFormatter
from expenses.models import UsageTag, Expense
from expenses.serializers import UsageTagSerializer, ExpenseSerializer


class ExpenseTestCase(DateTimeFormatter, TestCase):

    def setUp(self):
        self.currency = Currency.objects.create(country='UGANDA', code='UGX', symbol='USh')
        self.user = User.objects.create(
            username='fin',
            email='tyne@tfinance.io',
            currency=self.currency
        )
        self.account_type = AccountType.objects.create(name='Mobile Money', code='MNO')
        self.account = Account.objects.create(
            account_type=self.account_type,
            user=self.user,
            account_number='01',
            account_provider='SAF',
        )
        self.account_2 = Account.objects.create(
            account_type=self.account_type,
            user=self.user,
            account_number='02',
            account_provider='SAF',
        )
        self.tag = UsageTag.objects.create(title='Rent', code='RNT')
        self.expense = Expense.objects.create(
            account=self.account,
            planned=True,
            narration="I need a roof",
            amount=6000,
            date_occurred='2020-03-23'
        )
        self.expense.tags.add(self.tag)

    def test_usage_tag(self):
        self.assertDictEqual(
            {
                'title': 'Rent',
                'code': 'RNT'
            },
            UsageTagSerializer(instance=self.tag).data
        )

    def test_expense_serializer(self):
        self.assertDictEqual(
            ExpenseSerializer(instance=self.expense).data,
            {
                'tags': [{'title': 'Rent', 'code': 'RNT'}],
                'account': {
                    'account_type': AccountTypeSerializer(self.account_type).data,
                    'account_number': '01',
                    'user': UserSerializer(self.user).data,
                    'account_provider': 'SAF',
                    'date_added': self.datetime_timezone_str(self.account.date_added),
                    'date_modified': self.datetime_timezone_str(self.account.date_modified),
                    'balance': 0,
                    'last_balance_update': None,
                    'active': False,
                },
                'planned': True,
                'narration': 'I need a roof',
                'amount': 6000,
                'date_occurred': '2020-03-23',
                'transaction_charge': 0,
                'date_created': self.datetime_timezone_str(self.expense.date_created)
            }
        )

    def test_expense_serializer_edit(self):
        # date occurred cannot be in the future
        exp = ExpenseSerializer(data={
            'date_occurred': self.future_date(1).strftime('%Y-%m-%d')
        }, instance=self.expense)
        self.assertFalse(exp.is_valid())
        self.assertListEqual(['date_occurred'], list(exp.errors.keys()))

        # correct date occurred
        dt = self.past_date(1)
        exp = ExpenseSerializer(data={
            'date_occurred': dt.strftime('%Y-%m-%d')
        }, instance=self.expense)
        self.assertTrue(exp.is_valid())
        expense = exp.save()
        self.assertEquals(expense.date_occurred, dt.date())

        # an account id that does not exist
        exp = ExpenseSerializer(data={
            'account_id': 2000
        }, instance=self.expense)
        self.assertFalse(exp.is_valid())
        self.assertListEqual(['account_id'], list(exp.errors.keys()))

        # a correct account ID
        exp = ExpenseSerializer(data={
            'account_id': self.account_2.pk
        }, instance=self.expense)
        self.assertTrue(exp.is_valid())
        expense = exp.save()
        self.assertEquals(expense.account, self.account_2)

    def test_expense_serializer_create(self):
        exp = ExpenseSerializer(data={
            'date_occurred': self.future_date(3).strftime('%Y-%m-%d'),
            'narration': 'test',
            'amount': 3000,
            'planned': True,
            'account_id': 100
        })
        self.assertFalse(exp.is_valid())
        self.assertListEqual(['account_id', 'date_occurred'], list(exp.errors.keys()))

        exp = ExpenseSerializer(data={
            'date_occurred': self.past_date(3).strftime('%Y-%m-%d'),
            'narration': 'test',
            'amount': 3000,
            'planned': True,
            'account_id': self.account.pk
        })
        self.assertTrue(exp.is_valid())
        expense = exp.save()
        self.assertIsNotNone(expense)
        self.assertEquals(expense.date_occurred, self.past_date(3).date())
        self.assertEquals(expense.narration, 'test')
        self.assertEquals(expense.amount, 3000)
        self.assertTrue(self.account.expense_set.filter(pk=expense.pk).exists())
