from typing import Dict

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils import timezone, translation
from rest_framework.fields import IntegerField

from core.serializers import NoEditOrCreateModelSerializer, ModelSerializerRequiredFalsifiable, AccountSerializer, Cache
from core.models import Account
from .models import UsageTag, Expense


class ValidateRecItems(Cache):

    def validate_account_id(self, value: int):
        try:
            self._cache.update({
                'account': Account.objects.get(pk=value)
            })
        except ObjectDoesNotExist:
            raise ValidationError(
                translation.gettext_lazy(f'No account with ID: {value}')
            )
        return value


class UsageTagSerializer(NoEditOrCreateModelSerializer):

    class Meta:
        model = UsageTag
        exclude = ('id',)


class ExpenseSerializer(ValidateRecItems, ModelSerializerRequiredFalsifiable):
    tags = UsageTagSerializer(many=True, read_only=True)
    account = AccountSerializer(read_only=True)
    account_id = IntegerField(write_only=True)

    class Meta:
        model = Expense
        exclude = ('id',)

    @staticmethod
    def validate_date_occurred(value: timezone.datetime):
        if value > timezone.now().date():
            raise ValidationError(
                translation.gettext_lazy('Date of expense cannot be in the future')
            )
        return value

    def update_account_value(self, validated_data: Dict):
        if 'account' in self._cache and 'account_id' in validated_data:
            validated_data.update({'account': self._cache.get('account')})
        return validated_data

    def update(self, instance, validated_data):
        return super().update(instance, self.update_account_value(validated_data))

    def create(self, validated_data):
        return super().create(self.update_account_value(validated_data))
