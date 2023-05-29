from django.test import TestCase
from django.core.exceptions import PermissionDenied

from core.models import Currency, User, Account, AccountType
from core.serializers import CurrencySerializer, NoEditOrCreateModelSerializer, AccountTypeSerializer


class CoreSerializerTestCase(TestCase):

    def setUp(self) -> None:
        self.currency = Currency.objects.create(country='Kenya', code='KES', symbol='Ksh')
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
