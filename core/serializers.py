from typing import Dict

from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from rest_framework.serializers import ModelSerializer, IntegerField, ValidationError
from rest_framework.fields import empty

from .models import User, Currency, Account, AccountType


class NoEditOrCreateModelSerializer(ModelSerializer):

    def create(self, validated_data):
        raise PermissionDenied(_('Cannot add'))

    def update(self, instance, validated_data):
        raise PermissionDenied(_('Cannot update'))


class CurrencySerializer(NoEditOrCreateModelSerializer):

    class Meta:
        model = Currency
        fields = ('country', 'code')


class AccountTypeSerializer(NoEditOrCreateModelSerializer):

    class Meta:
        model = AccountType
        fields = ('name', 'code')


class UserSerializer(ModelSerializer):
    user_currency = CurrencySerializer(source='currency', required=False)
    currency = IntegerField(required=True, write_only=True)
    __cache = {}

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)

        if instance:
            for field in self.fields.values():
                if hasattr(field, 'required'):
                    field.required = False

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'is_active', 'currency', 'password', 'user_currency')
        extra_kwargs = {
            'password': {'write_only': True},
            'is_active': {'read_only': True}
        }

    def validate_currency(self, value):
        try:
            self.__cache.update({
                'currency': Currency.objects.get(pk=value)
            })
        except ObjectDoesNotExist:
            raise ValidationError(_(f'No currency with id "{value}"'))

    def update_validated_data_with_currency(self, validated_data: Dict):
        if currency := self.__cache.get('currency'):
            validated_data.update({'currency': currency})
        else:
            raise ObjectDoesNotExist(_('No currency found'))

        return validated_data

    def create(self, validated_data: Dict) -> User:
        return super().create(
            self.update_validated_data_with_currency(validated_data)
        )

    def update(self, instance, validated_data: Dict):
        if 'currency' in validated_data.keys():
            validated_data = self.update_validated_data_with_currency(
                validated_data
            )
        return super().update(instance, validated_data)
