from typing import Dict, OrderedDict, Callable

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils import timezone, translation
from rest_framework.fields import IntegerField
from rest_framework.serializers import ModelSerializer

from core.serializers import NoEditOrCreateModelSerializer, ModelSerializerRequiredFalsifiable,\
    AccountSerializer, UserSerializer, NoEditModelSerializer
from core.models import Account, User
from core.utils import DateTimeFormatter
from .models import UsageTag, Expense, RecurringPayment, Transaction, TransactionActions
from .validators import RenewalDateValidator


class ValidateRecItems(DateTimeFormatter):
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

    def start_and_end_date_validations(self, validated_data: OrderedDict, instance):
        if 'end_date' in validated_data:
            e_date = validated_data.get('end_date')
            s_date = instance.start_date if instance else validated_data.get('start_date')

            # start date is greater than end date
            if self.make_date(s_date) > self.make_date(e_date):
                raise ValidationError({
                    'end_date': translation.gettext_lazy('End date cannot be greater than end date')
                })


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

    # TODO apparently you dont need this
    def update(self, instance, validated_data):
        return super().update(instance, self.update_account_value(validated_data))

    # TODO apparently you dont need this
    def create(self, validated_data):
        return super().create(self.update_account_value(validated_data))


class PaymentSerializer(ValidateRecItems, ModelSerializerRequiredFalsifiable):
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
        self.start_and_end_date_validations(validated_data, self.instance)
        return validated_data


class TransactionSerializer(ValidateRecItems, TransactionActions, NoEditModelSerializer, ModelSerializer):
    account = AccountSerializer(read_only=True)
    account_id = IntegerField(write_only=True)

    class Meta:
        model = Transaction
        fields = '__all__'

    def validate(self, attrs):
        if self.instance:
            raise ValidationError(translation.gettext_lazy('Cannot update transactions'))

        validated_data: OrderedDict = super().validate(attrs)
        self.transaction_cleaner(
            self._cache.get('account'),
            validated_data.get('transaction_type'),
            validated_data.get('transaction_for'),
            validated_data.get('transaction_for_id'),
            False
        )
        return validated_data
