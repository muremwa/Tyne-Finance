from typing import Dict, OrderedDict, Callable

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils import timezone, translation
from rest_framework.fields import IntegerField

from core.serializers import NoEditOrCreateModelSerializer, ModelSerializerRequiredFalsifiable,\
    AccountSerializer, UserSerializer
from core.models import Account, User
from core.utils import DateTimeFormatter
from .models import UsageTag, Expense, RecurringPayment
from .validators import RenewalDateValidator


class ValidateRecItems:
    _cache = {}

    def master_validator(self, key: str, query_func: Callable, message: str):
        try:
            self._cache.update({
                key: query_func()
            })
        except ObjectDoesNotExist:
            raise ValidationError(
                translation.gettext_lazy(message)
            )

    def validate_account_id(self, value: int):
        self.master_validator(
            'account',
            lambda: Account.objects.get(pk=value),
            f'No Account with ID {value}'
        )
        return value

    def validate_user_id(self, value: int):
        self.master_validator(
            'user',
            lambda: User.objects.get(pk=value),
            f'No user account with ID {value}'
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


class PaymentSerializer(ValidateRecItems, DateTimeFormatter, ModelSerializerRequiredFalsifiable):
    tags = UsageTagSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    user_id = IntegerField(write_only=True)

    class Meta:
        model = RecurringPayment
        fields = '__all__'
        read_only_fields = ('renewal_count',)
        extra_kwargs = {
            'renewal_date': {
                'validators': [RenewalDateValidator('12-31')]
            }
        }

    def validate(self, attrs):
        validated_data: OrderedDict = super().validate(attrs)

        if 'end_date' in validated_data:
            e_date = validated_data.get('end_date')
            s_date = self.instance.start_date if self.instance else validated_data.get('start_date')

            # start date is greater than end date
            if self.make_date(s_date) > self.make_date(e_date):
                raise ValidationError({
                    'end_date': translation.gettext_lazy('End date cannot be greater than end date')
                })

        return validated_data
