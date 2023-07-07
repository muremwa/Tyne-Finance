from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import PermissionDenied, ValidationError, ObjectDoesNotExist

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


class TransactionCleaner:

    @staticmethod
    def transaction_cleaner(account: Account, transaction_type: str, transaction_for: str, for_id: int, is_model=True):
        """
            Clean a transaction

            - Account must be active
            - Credit transactions cannot have expense or payments as they are the opposite of a cost
            - Transaction for and id must exist together, cannot have one without the other
            - for ID must point to an existing item

        """
        if not account.active:
            raise ValidationError({
                'account' if is_model else 'account_id': _('The selected account is not active')
            })

        if transaction_type == 'CD':
            if transaction_for or for_id is not None:
                item_type = 'an Expense' if transaction_for == "EX" else 'a Payment'
                raise ValidationError({
                    'transaction_type': _(f'Credit transactions cannot have {item_type}')
                })

        if transaction_for:
            if for_id is None:
                raise ValidationError({
                    'transaction_for_id': _('ID for the transaction item needed')
                })
            else:
                klass = Expense if transaction_for == 'EX' else RecurringPayment
                try:
                    klass.objects.get(pk=for_id)
                except ObjectDoesNotExist:
                    item_type = 'Expense' if transaction_for == "EX" else 'Payment'
                    raise ValidationError({
                        'transaction_for_id': _(f'{item_type} with ID {for_id} does not exist')
                    })
        else:
            if for_id is not None:
                raise ValidationError({
                    'transaction_for': _('Required')
                })


class Transaction(TransactionCleaner, models.Model):
    """
        debit means you'll remove money from the account, credit vice versa
    """
    TRANSACTION_FOR_CHOICES = (('EX', 'Expense'), ('RP', 'Recurring Payment'))
    TRANSACTION_TYPE_CHOICES = (('DB', 'Debit'), ('CD', 'Credit'))

    transaction_type = models.CharField(max_length=2, choices=TRANSACTION_TYPE_CHOICES)
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    amount = models.IntegerField()
    automatic = models.BooleanField(default=False)
    transaction_date = models.DateTimeField(auto_now_add=True)
    transaction_for = models.CharField(max_length=2, choices=TRANSACTION_FOR_CHOICES, null=True, blank=True)
    transaction_for_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'Transaction: {self.transaction_type} • ({self.amount})'

    def __repr__(self):
        return f'<Transaction: {self.transaction_type} ({self.amount})>'

    def get_transaction_item(self):
        item: Expense | RecurringPayment | None = None

        if self.transaction_for and self.transaction_for_id is not None:
            if self.transaction_for == 'EX':
                item = Expense.objects.get(pk=self.transaction_for_id)

            elif self.transaction_for == 'RP':
                item = RecurringPayment.objects.get(pk=self.transaction_for_id)

        return item

    def clean(self):
        self.transaction_cleaner(self.account, self.transaction_type, self.transaction_for, self.transaction_for_id)
        return super().clean()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.pk:
            raise PermissionDenied('Cannot update a transaction')

        super().save(force_insert, force_update, using, update_fields)

        # reflect status on account
        if self.transaction_type == 'DB':
            self.account.balance -= self.amount
        else:
            self.account.balance += self.amount
        self.account.last_balance_update = timezone.now()
        self.account.save()
        return self

    def delete(self, using=None, keep_parents=False):
        if self.transaction_type == 'DB':
            self.account.balance += self.amount
        else:
            self.account.balance -= self.amount
        self.account.last_balance_update = timezone.now()
        self.account.save()
        return super().delete(using=None, keep_parents=False)
