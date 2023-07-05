from django.test import TestCase

from core.models import User, Currency
from core.utils import DateTimeFormatter
from core.serializers import UserSerializer
from expenses.models import UsageTag
from budgets.models import BudgetItem, WishListItem
from budgets.serializers import BudgetItemSerializer, WishListItemSerializer


class BudgetTestCases(DateTimeFormatter, TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='tyne',
            email='tyne@tfinance.io',
            currency=Currency.objects.create(country='Libya', code='LYD', symbol='L')
        )
        self.user_2 = User.objects.create(
            username='vine',
            email='vine@tfinance.io',
            currency=Currency.objects.create(country='Kenya', code='KES', symbol='Ksh')
        )
        self.budget_item = BudgetItem.objects.create(
            user=self.user,
            start_date='2020-01-01',
            end_date='2020-12-01',
            name='Fare'
        )
        self.tag = UsageTag.objects.create(title='Transport', code='TP')
        self.budget_item.tags.add(self.tag)
        self.wish_list_item = WishListItem.objects.create(
            user=self.user,
            name='Car',
            due_date='2021-03-10'
        )

    def test_budget_item(self):
        self.assertDictEqual(
            BudgetItemSerializer(self.budget_item).data,
            {
                'id': self.budget_item.pk,
                'user': UserSerializer(self.budget_item.user).data,
                'start_date': '2020-01-01',
                'end_date': '2020-12-01',
                'name': 'Fare',
                'narration': '',
                'tags': [{'title': 'Transport', 'code': 'TP'}],
                'amount': 0,
                'date_added': self.datetime_timezone_str(self.budget_item.date_added),
                'date_modified': self.datetime_timezone_str(self.budget_item.date_modified)
            }
        )

    def test_wish_list_item(self):
        self.assertDictEqual(
            WishListItemSerializer(self.wish_list_item).data,
            {
                'id': self.wish_list_item.pk,
                'user': UserSerializer(self.wish_list_item.user).data,
                'name': 'Car',
                'due_date': '2021-03-10',
                'price': 0,
                'granted': False,
                'narration': '',
                'date_added': self.datetime_timezone_str(self.wish_list_item.date_added),
                'date_modified': self.datetime_timezone_str(self.wish_list_item.date_modified)
            }
        )

    def test_items_edit(self):
        items = [
            lambda d: BudgetItemSerializer(data=d, instance=self.budget_item),
            lambda d: WishListItemSerializer(data=d, instance=self.wish_list_item)
        ]

        # wrong end date on BudgetItem
        ser = items[0]({'end_date': self.past_date(20).strftime('%Y-%m-%d')})
        self.assertFalse(ser.is_valid())
        self.assertListEqual(['end_date'], list(ser.errors.keys()))

        nd = self.future_date(20)
        ser = items[0]({'end_date': nd.strftime('%Y-%m-%d')})
        self.assertTrue(ser.is_valid())
        ser_item = ser.save()
        self.assertEquals(ser_item.pk, self.budget_item.pk)
        self.assertEquals(nd.date(), self.budget_item.end_date)

        # test user IDs
        for itemFunc in items:
            ser_2 = itemFunc({'user_id': 3000})
            self.assertFalse(ser_2.is_valid())
            self.assertListEqual(['user_id'], list(ser_2.errors.keys()))

            ser_2 = itemFunc({'user_id': self.user_2.pk})
            self.assertTrue(ser_2.is_valid())
            ser_item_2 = ser_2.save()
            self.assertEquals(ser_item_2.pk, self.budget_item.pk)
            self.assertEquals(ser_item_2.user.pk, self.user_2.pk)

    def test_items_new(self):
        items = [
            BudgetItemSerializer(data={
                'start_date': '2020-01-01',
                'end_date': '2020-12-01',
                'name': 'RENT',
                'user_id': self.user_2.pk,
                'narration': 'SAMPLE'
            }),
            WishListItemSerializer(data={
                'user_id': self.user_2.pk,
                'name': 'TV',
                'narration': 'SAMPLE',
                'due_date': '2021-03-10'
            })
        ]
        q_sets = [
            lambda p: self.user_2.budgetitem_set.filter(pk=p).exists(),
            lambda p: self.user_2.wishlistitem_set.filter(pk=p).exists()
        ]

        for ser, q_set in zip(items, q_sets):
            self.assertTrue(ser.is_valid())
            item = ser.save()
            self.assertIsNotNone(item)
            self.assertTrue(q_set(item.pk))
