from typing import Dict, OrderedDict

from django.contrib.auth.hashers import make_password
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from rest_framework.serializers import ModelSerializer, IntegerField, CharField, ValidationError
from rest_framework.fields import empty

from .models import User, Currency, Account, AccountType


class Cache:
    _cache = {}


class NoCreateModelSerializer:

    def create(self, validated_data):
        raise PermissionDenied(_('Cannot add'))


class NoEditModelSerializer:

    def update(self, instance, validated_data):
        raise PermissionDenied(_('Cannot update'))


class NoEditOrCreateModelSerializer(NoCreateModelSerializer, NoEditModelSerializer, ModelSerializer):
    pass


class ModelSerializerRequiredFalsifiable(ModelSerializer):
    """
        If there is an instance, the fields are all marked as not required
        
        Has cache to store items
    """

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)

        if instance:
            for field in self.fields.values():
                if hasattr(field, 'required'):
                    field.required = False
    

class CurrencySerializer(NoEditOrCreateModelSerializer):

    class Meta:
        model = Currency
        fields = ('country', 'code')


class AccountTypeSerializer(NoEditOrCreateModelSerializer):

    class Meta:
        model = AccountType
        fields = ('name', 'code')


class UserSerializer(Cache, ModelSerializerRequiredFalsifiable):
    user_currency = CurrencySerializer(source='currency', required=False)
    currency = IntegerField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'is_active', 'currency', 'password', 'user_currency')
        extra_kwargs = {
            'password': {'write_only': True},
            'is_active': {'read_only': True}
        }

    def validate_currency(self, value):
        try:
            self._cache.update({
                'currency': Currency.objects.get(pk=value)
            })
        except ObjectDoesNotExist:
            raise ValidationError(_(f'No currency with id "{value}"'))
        return value

    def update_validated_data_with_currency(self, validated_data: Dict):
        if currency := self._cache.get('currency'):
            validated_data.update({'currency': currency})
        else:
            raise ObjectDoesNotExist(_('No currency found'))

        return validated_data

    @staticmethod
    def update_validated_data_with_password(data: Dict):
        if password := data.get('password'):
            data.update({
                'password': make_password(password)
            })
        return data

    def create(self, validated_data: Dict) -> User:
        return super().create(
            self.update_validated_data_with_password(
                self.update_validated_data_with_currency(validated_data)
            )
        )

    def update(self, instance: User, validated_data: Dict):
        if 'currency' in validated_data:
            validated_data = self.update_validated_data_with_currency(
                validated_data
            )

        if 'password' in validated_data:
            validated_data = self.update_validated_data_with_password(
                validated_data
            )

        return super().update(instance, validated_data)


class AccountSerializer(Cache, NoEditModelSerializer, ModelSerializer):
    account_type = AccountTypeSerializer(read_only=True)
    account_type_code = CharField(max_length=10, write_only=True)
    user = UserSerializer(read_only=True)
    user_id = IntegerField(write_only=True)

    class Meta:
        model = Account
        exclude = ('id',)

    def validate(self, attrs: OrderedDict):
        validated_data: OrderedDict = super().validate(attrs)

        validation_items = {
            'user': {
                'field': 'user_id',
                'query': lambda: User.objects.get(pk=validated_data.get("user_id")),
                'message': f'No user with ID {validated_data.get("user_id")}'
            },
            'account_type': {
                'field': 'account_type_code',
                'query': lambda: AccountType.objects.get(code=validated_data.get("account_type_code")),
                'message': f'No account type code {validated_data.get("account_type_code")}'
            }
        }

        for key, details in validation_items.items():
            try:
                self._cache.update({
                    key: details['query']()
                })
            except ObjectDoesNotExist:
                raise ValidationError({
                    details['field']: _(details['message'])
                })

        # validate the uniques of the account
        q_set = Account.objects.filter(
            account_provider=validated_data.get('account_provider'),
            account_number=validated_data.get('account_number'),
            account_type__code=validated_data.get('account_type_code')
        )

        if q_set.exists():
            raise ValidationError(_('Account not unique'))

        return validated_data

    def create(self, validated_data: Dict):
        fields_replacements = {
            'account_type_code': 'account_type',
            'user_id': 'user'
        }

        for write_key, field_key in fields_replacements.items():
            if write_key in validated_data and field_key in self._cache:
                validated_data.update({
                    field_key: self._cache.get(field_key)
                })
                validated_data.pop(write_key)

        return super().create(validated_data)
