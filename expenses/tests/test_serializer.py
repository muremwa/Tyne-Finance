from django.test import TestCase

from core.models import Currency, User, Account, AccountType
from core.serializers import AccountTypeSerializer, UserSerializer
from core.utils import DateTimeFormatter
from expenses.models import UsageTag, Expense, RecurringPayment
from expenses.serializers import UsageTagSerializer, ExpenseSerializer, PaymentSerializer


class ExpenseTestCase(DateTimeFormatter, TestCase):

    def setUp(self):
        self.currency = Currency.objects.create(country='UGANDA', code='UGX', symbol='USh')
        self.user = User.objects.create(
            username='fin',
            email='tyne@tfinance.io',
            currency=self.currency
        )
        self.user_2 = User.objects.create(
            username='gin',
            email='gin@tfinance.io',
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
        self.payment = RecurringPayment.objects.create(
            user=self.user,
            narration='landlord',
            amount=500,
            start_date='2020-01-06',
            renewal_date='10',
        )
        self.payment.tags.add(self.tag)

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

    def test_payment_serializer(self):
        self.assertDictEqual(
            PaymentSerializer(instance=self.payment).data,
            {
                'id': self.payment.pk,
                'tags': [{'title': 'Rent', 'code': 'RNT'}],
                'user': {
                    'username': self.user.username,
                    'first_name': self.user.first_name,
                    'last_name': self.user.last_name,
                    'email': self.user.email,
                    'is_active': self.user.is_active,
                    'user_currency': {
                        'country': self.currency.country,
                        'code': self.currency.code
                    }
                },
                'narration': 'landlord',
                'amount': 500,
                'transaction_charge': 0,
                'start_date': '2020-01-06',
                'end_date': None,
                'renewal_date': '10',
                'renewal_count': 0,
                'date_added': self.datetime_timezone_str(self.payment.date_added),
                'date_modified': self.datetime_timezone_str(self.payment.date_modified)
            }
        )

    def test_payment_serializer_edit(self):
        # date occurred cannot be in the future
        pays = PaymentSerializer(data={
            'end_date': self.past_date(10).strftime('%Y-%m-%d')
        }, instance=self.payment)
        self.assertFalse(pays.is_valid())
        self.assertListEqual(['end_date'], list(pays.errors.keys()))

        # correct date occurred
        dt = self.past_date(1)
        pays = PaymentSerializer(data={
            'end_date': dt.strftime('%Y-%m-%d')
        }, instance=self.payment)
        self.assertTrue(pays.is_valid())
        pays.save()
        self.assertEquals(self.payment.end_date, dt.date())

        # a user id that does not exist
        pays = PaymentSerializer(data={
            'user_id': 2000
        }, instance=self.payment)
        self.assertFalse(pays.is_valid())
        self.assertListEqual(['user_id'], list(pays.errors.keys()))

        # a correct account ID
        pays = PaymentSerializer(data={
            'user_id': self.user_2.pk
        }, instance=self.payment)
        self.assertTrue(pays.is_valid())
        pays.save()
        self.assertEquals(self.payment.user.pk, self.user_2.pk)
