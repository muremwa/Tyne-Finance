from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework.authtoken.models import Token


class Currency(models.Model):
    country = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    symbol = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'currencies'
        unique_together = (('country', 'code'),)

    def __repr__(self):
        return f'<Currency: {self.country}({self.code})>'

    def __str__(self):
        return f'{self.country} ({self.code})'


class User(AbstractUser):
    currency = models.ForeignKey(Currency, on_delete=models.RESTRICT, null=True)

    def get_user_auth_token(self):
        token = None
        if self.pk:
            tokens = Token.objects.filter(user=self.pk)
            token = tokens[0] if tokens.exists() else Token.objects.create(user=self)
        return token

    def __repr__(self):
        return f'<CoreUser: {self.username}>'

    def __str__(self):
        return f'{self.username} ({self.email})'


class AccountType(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)

    def __repr__(self):
        return f'<AccountType: {self.name}>'

    def __str__(self):
        return f'{self.name}'


class Account(models.Model):
    account_type = models.ForeignKey(AccountType, on_delete=models.RESTRICT)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_provider = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    balance = models.IntegerField(default=0)
    last_balance_update = models.DateTimeField(blank=True, null=True)
    active = models.BooleanField(default=False)

    class Meta:
        unique_together = (('account_provider', 'account_number', 'account_type'),)

    def __repr__(self):
        return f'<Account: {self.user.username}>'

    def __str__(self):
        return f'Acc({self.user.username} • {self.account_number } • {self.account_type} • {self.account_provider})'
