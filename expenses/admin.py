from django.contrib import admin

from .models import UsageTag, Expense, RecurringPayment, Transaction


@admin.register(UsageTag)
class UsageTagModelAdmin(admin.ModelAdmin):
    list_display = ('title', 'code')
    search_fields = ('title', 'code')
    actions = None

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ModelAdminWithoutAccountFormFieldExtras(admin.ModelAdmin):

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if account_field := form.base_fields.get('account'):
            account_field.widget.can_add_related = False
            account_field.widget.can_change_related = False
            account_field.widget.can_delete_related = False
            account_field.widget.can_view_related = False

        return form


@admin.register(Expense)
class ExpenseModelAdmin(ModelAdminWithoutAccountFormFieldExtras):
    fieldsets = [
        (
            'Expense Info', {
                'fields': ['narration', 'tags', 'planned', 'user']
            }
        ),
        (
            'Expense Finances', {
                'fields': ['amount']
            }
        ),
        (
            'Expense Dates', {
                'fields': ['date_created', 'date_occurred']
            }
        )
    ]
    readonly_fields = ['date_created']
    list_filter = ['planned', 'tags']
    list_display = ['pk', 'date_occurred', 'planned', 'amount', 'user']
    list_display_links = ['date_occurred', 'pk']
    actions = None


@admin.register(RecurringPayment)
class PaymentModelAdmin(ModelAdminWithoutAccountFormFieldExtras):
    fieldsets = [
        (
            'Payment Info', {
                'fields': ['narration', 'tags', 'renewal_count', 'user']
            }
        ),
        (
            'Payment Finances', {
                'fields': ['amount']
            }
        ),
        (
            'Payment Dates', {
                'fields': ['renewal_date', 'start_date', 'end_date']
            }
        ),
        (
            'Misc', {
                'fields': ['date_added', 'date_modified']
            }
        )
    ]
    readonly_fields = ['date_added', 'date_modified', 'renewal_count']
    list_filter = ['start_date', 'tags']
    list_display = ['pk', 'start_date', 'renewal_count', 'is_annual', 'amount']
    list_display_links = ['pk', 'start_date']
    actions = None


@admin.register(Transaction)
class TransactionModelAdmin(ModelAdminWithoutAccountFormFieldExtras):
    fieldsets = [
        (
            'Transaction Information', {
                'fields': ['transaction_date', 'transaction_type', 'amount', 'transaction_charge', 'account', 'automatic']
            }
        ),
        (
            'Transaction Item Details', {
                'fields': ['transaction_for', 'transaction_for_id']
            }
        )
    ]
    readonly_fields = ('transaction_date', 'automatic')
    list_display = ['id', 'transaction_date', 'transaction_type', 'amount', 'transaction_charge', 'get_account_name', 'automatic']
    list_filter = ['transaction_type', 'automatic']
    actions = None

    def get_account_name(self, obj: Transaction):
        return f'{obj.account.account_number} • {obj.account.account_provider}'

    get_account_name.short_description = 'Account'

    def has_change_permission(self, request, obj=None):
        return False
