from django.test import TestCase
from django.core.exceptions import ValidationError

from core.models import Currency, User
from expenses.models import UsageTag
from budgets.models import BudgetItem, WishListItem


class BudgetTestCase(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(
            username='tyne',
            email='tyne@tfinance.io',
            currency=Currency.objects.create(country='Kenya', code='KES', symbol='Ksh')
        )

    def test_budget_item(self):
        item = BudgetItem.objects.create(
            user=self.user,
            start_date='2020-01-01',
            end_date='2020-12-01',
            name='Fare'
        )
        item.tags.add(UsageTag.objects.create(title='Transport', code='TP'))
        self.assertIs(item.amount, 0)
        self.assertIsNotNone(item.date_added)
        self.assertIsNotNone(item.date_modified)

        item.end_date = '2010-12-01'
        self.assertRaisesMessage(
            ValidationError,
            'End date should be after start date',
            item.clean,
        )

    def test_wish_list_item(self):
        item = WishListItem.objects.create(
            user=self.user,
            name='Car',
            due_date='2021-03-10'
        )
        self.assertIs(item.price, 0)
        self.assertIsNotNone(item.date_added)
        self.assertIsNotNone(item.date_modified)
        self.assertFalse(item.granted)
