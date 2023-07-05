from typing import OrderedDict

from rest_framework.fields import IntegerField

from core.serializers import ModelSerializerRequiredFalsifiable, UserSerializer
from expenses.serializers import ValidateRecItems, UsageTagSerializer

from .models import BudgetItem, WishListItem


class BudgetItemSerializer(ValidateRecItems, ModelSerializerRequiredFalsifiable):
    tags = UsageTagSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    user_id = IntegerField(write_only=True)

    class Meta:
        model = BudgetItem
        fields = '__all__'

    def validate(self, attrs):
        validated_data: OrderedDict = super().validate(attrs)
        self.start_and_end_date_validations(validated_data, self.instance)
        return validated_data


class WishListItemSerializer(ValidateRecItems, ModelSerializerRequiredFalsifiable):
    user = UserSerializer(read_only=True)
    user_id = IntegerField(write_only=True)

    class Meta:
        model = WishListItem
        fields = '__all__'
