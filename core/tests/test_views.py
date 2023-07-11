from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from core.models import Currency, User, AccountType, Account


class CoreViewsTestCaseNoAuth(TestCase):

    def setUp(self) -> None:
        self.currency = Currency.objects.create(country='Barbados', code='BBD', symbol='$')
        self.currency_2 = Currency.objects.create(country='Bahamas', code='BSD', symbol='$')
        self.user = User.objects.create(
            username='rih',
            email='rih@tfinance.io',
            currency=self.currency,
        )
        self.user.set_password('test@123')
        self.user.save()
        self.user_2 = User.objects.create(
            username='van',
            email='van@tfinance.io',
            currency=self.currency,
            is_active=False
        )
        self.user_2.set_password('test@123')
        self.user_2.save()
        self.account_type = AccountType.objects.create(name='Mobile Money', code='MNO')
        self.account_type_2 = AccountType.objects.create(name='BANK', code='BNK')
        self.account = Account.objects.create(
            account_type=self.account_type,
            user=self.user,
            account_number='01',
            account_provider='SAF',
        )
        self.client = APIClient()

    def test_login_view(self):
        self.assertEquals(400, self.client.post('/core/auth/login/').status_code)

        self.assertEquals(
            401,
            self.client.post(
                '/core/auth/login/',
                {'username': self.user_2.username, 'password': 'test@123'}
            ).status_code
        )
        self.assertEquals(
            401,
            self.client.post('/core/auth/login/', {'username': 'rih', 'password': 'test@1234'}).status_code
        )
        self.assertIsNone(self.user.last_login)
        req = self.client.post('/core/auth/login/', {'username': 'rih', 'password': 'test@123'})
        self.assertEquals(200, req.status_code)
        self.assertListEqual(['message', 'success', 'token', 'user'], list(req.json().keys()))
        self.user.refresh_from_db(fields=['last_login'])
        self.assertIsNotNone(self.user.last_login)

    def test_sign_up(self):
        req = self.client.post('/core/auth/sign-up/')
        self.assertEquals(400, req.status_code)
        self.assertFalse(req.json().get('success'))
        self.assertTrue('errors' in req.json())

        req = self.client.post(
            '/core/auth/sign-up/',
            {'username': 'jim', 'password': 'test@123', 'currency': self.currency.pk}
        )
        self.assertEquals(201, req.status_code)
        self.assertTrue(req.json().get('success'))
        self.assertTrue('user' in req.json())
        self.assertTrue('token' in req.json())


class CoreViewsTestCase(CoreViewsTestCaseNoAuth):

    def setUp(self) -> None:
        super().setUp()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user.get_user_auth_token().key}')

    def test_logout(self):
        self.assertTrue(Token.objects.filter(user=self.user).exists())
        self.assertEquals(200, self.client.post('/core/auth/logout/').status_code)
        self.assertFalse(Token.objects.filter(user=self.user).exists())

    def test_refresh_token(self):
        pv_tk = self.user.get_user_auth_token()
        req = self.client.post('/core/auth/refresh-token/')
        self.assertEquals(200, req.status_code)
        self.assertNotEquals(pv_tk.key, req.json().get('token'))
        self.assertFalse(Token.objects.filter(pk=pv_tk.pk).exists())
