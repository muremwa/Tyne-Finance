from datetime import datetime

from django.core.validators import BaseValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


class RenewalDateValidator(BaseValidator):

    @staticmethod
    def validate_day(val):
        if val > 31:
            raise ValidationError(_('Dates should not exceed 31'))

    @staticmethod
    def validate_month(val):
        if val > 12:
            raise ValidationError(_('Months should not exceed 12'))

    def __call__(self, value: str):
        try:
            if '-' in value:
                if len(value) != 5:
                    raise ValidationError('Use the correct format for annual renewal')

                vals = [int(val) for val in value.split('-')]
                for func, val in zip([self.validate_month, self.validate_day], vals):
                    func(val)

                try:
                    datetime(1970, vals[0], vals[1])
                except ValueError:
                    raise ValidationError(_('Use a valid date'))

            else:
                self.validate_day(int(value))
        except ValueError:
            raise ValidationError(_('Use appropriate numbers'))
