from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from expenses.models import UsageTag
from core.models import User


class BudgetItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    name = models.CharField(max_length=50)
    narration = models.TextField()
    tags = models.ManyToManyField(UsageTag)
    amount = models.IntegerField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError({
                'end_date': _('End date should be after start date')
            })

    def __repr__(self):
        return f'<BudgetItem: {self.name}>'

    def __str__(self):
        return f'{self.name} ({self.start_date} -> {self.end_date})'


class WishListItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    narration = models.TextField()
    price = models.IntegerField(default=0)
    granted = models.BooleanField(default=False)
    due_date = models.DateField()
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return f'<WishListItem: {self.name}>'

    def __str__(self):
        return f'{self.name} due {self.due_date}'
