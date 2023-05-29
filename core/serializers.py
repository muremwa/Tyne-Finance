from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _
from rest_framework.serializers import ModelSerializer

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
