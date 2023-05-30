from django.test import TestCase
from django.core.exceptions import PermissionDenied

from core.models import Currency, User, Account, AccountType
from core.serializers import CurrencySerializer, NoEditOrCreateModelSerializer, AccountTypeSerializer, UserSerializer


class CoreSerializerTestCase(TestCase):

    def setUp(self) -> None:
        self.currency = Currency.objects.create(country='Kenya', code='KES', symbol='Ksh')
        self.currency_2 = Currency.objects.create(country='Tanzania', code='TZS', symbol='Tsh')
        self.user = User.objects.create(
            username='tyne',
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

    def test_no_edit_or_update(self):
        self.assertRaises(
            PermissionDenied,
            NoEditOrCreateModelSerializer().create,
            {}
        )
        self.assertRaises(
            PermissionDenied,
            NoEditOrCreateModelSerializer().update,
            {},
            {}
        )

    def test_currency_serializer(self):
        curr = CurrencySerializer(self.currency)
        self.assertDictEqual(
            curr.data,
            {'country': 'Kenya', 'code': 'KES'}
        )

    def test_account_type_serializer(self):
        act = AccountTypeSerializer(self.account_type)
        self.assertDictEqual(
            act.data,
            {'name': self.account_type.name, 'code': self.account_type.code}
        )

    def test_user_serializer(self):
        us = UserSerializer(self.user)
        self.assertDictEqual(
            us.data,
            {
                'username': self.user.username,
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'email': self.user.email,
                'is_active': self.user.is_active,
                'user_currency': {
                    'country': self.currency.country,
                    'code': self.currency.code
                }
            }
        )

    def test_user_serializer_create(self):
        new_user = UserSerializer(data={
            'username': 'big',
            'email': 'big@tyne.com',
            'password': '12345',
            'currency': 1900
        })
        self.assertFalse(new_user.is_valid())
        new_user = UserSerializer(data={
            'username': 'big',
            'email': 'big@tyne.com',
            'password': '12345',
            'currency': self.currency.pk
        })
        self.assertTrue(new_user.is_valid())
        big_user = new_user.save()
        big_user_q: User = User.objects.get(username__iexact='big')
        self.assertIsNotNone(big_user)
        self.assertIsNotNone(big_user_q)
        self.assertEquals(big_user_q.pk, big_user.pk)
        self.assertEquals(big_user_q.currency.pk, big_user.currency.pk)

    def test_user_serializer_edit(self):
        ed_user = UserSerializer(data={
            'currency': 2000
        }, instance=self.user)
        self.assertFalse(ed_user.is_valid())
        ed_user = UserSerializer(data={
            'currency': self.currency_2.pk
        }, instance=self.user)
        self.assertTrue(ed_user.is_valid())
        self.assertEquals(self.user.currency.pk, self.currency.pk)
        bg_user = ed_user.save()
        self.user.refresh_from_db()
        self.assertEquals(bg_user.pk, self.user.pk)
        self.assertEquals(self.user.currency.pk, self.currency_2.pk)
        ed_user = UserSerializer(data={
            'username': 'jim'
        }, instance=self.user)
        self.assertTrue(ed_user.is_valid())
        ed_user.save()
        self.user.refresh_from_db()
        self.assertEquals(self.user.username, 'jim')
