from django.db import models

from core.models import Account, User
from .validators import RenewalDateValidator


class UsageTag(models.Model):
    title = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    def __repr__(self):
        return f'<UsageTag: {self.title}>'

    def __str__(self):
        return f'{self.title} ({self.code})'


class Expense(models.Model):
    tags = models.ManyToManyField(UsageTag)
    planned = models.BooleanField(default=False)
    narration = models.TextField()
    amount = models.IntegerField(default=0)
    transaction_charge = models.IntegerField(default=0)
    account = models.ForeignKey(Account, on_delete=models.RESTRICT)
    date_created = models.DateTimeField(auto_now_add=True)
    date_occurred = models.DateField()

    def __repr__(self):
        return f'<Expense: {self.date_occurred} ({self.amount + self.transaction_charge})>'

    def __str__(self):
        return f'Expense({self.date_occurred} • {self.amount + self.transaction_charge})'


class RecurringPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.RESTRICT)
    tags = models.ManyToManyField(UsageTag)
    narration = models.TextField()
    amount = models.IntegerField(default=0)
    transaction_charge = models.IntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    renewal_date = models.CharField(
        max_length=5,
        validators=[RenewalDateValidator('12-31')],
        help_text="Two digits, 01 | 31, monthly; Four Digits, 12-01, 12-31, annual (month-day)."
    )
    renewal_count = models.IntegerField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    @property
    def is_annual(self) -> bool:
        return '-' in self.renewal_date

    def __repr__(self):
        return f'<Payment: {"annual" if self.is_annual else "monthly"} ({self.amount + self.transaction_charge})>'

    def __str__(self):
        return f'Payment({"annual" if self.is_annual else "monthly"} • {self.amount + self.transaction_charge})'


# TODO: Add charges MODEL to keep track of charges made to accounts.
