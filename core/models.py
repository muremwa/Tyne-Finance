from django.db import models
from django.contrib.auth.models import AbstractUser


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

    def __repr__(self):
        return f'<CoreUser: {self.username}>'

    def __str__(self):
        return f'{self.username} ({self.email})'
