from django.test import TestCase
from django.core.exceptions import ValidationError

from expenses.validators import RenewalDateValidator


class ExpensesValidatorsTestCase(TestCase):

    def setUp(self) -> None:
        self.renewal_validator = RenewalDateValidator('MD')

    def test_validator(self):
        self.assertRaisesMessage(
            ValidationError,
            'Dates should not exceed 31',
            self.renewal_validator,
            '40'
        )
        self.assertRaisesMessage(
            ValidationError,
            'Use the correct format for annual renewal',
            self.renewal_validator,
            '23-+'
        )
        self.assertRaisesMessage(
            ValidationError,
            'Use a valid date',
            self.renewal_validator,
            '02-30'
        )
        self.assertRaisesMessage(
            ValidationError,
            'Use appropriate numbers',
            self.renewal_validator,
            'x'
        )
        self.assertRaisesMessage(
            ValidationError,
            'Dates should not exceed 31',
            self.renewal_validator,
            '01-40'
        )
        self.assertRaisesMessage(
            ValidationError,
            'Months should not exceed 12',
            self.renewal_validator,
            '19-60'
        )

