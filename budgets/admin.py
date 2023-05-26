from django.contrib import admin

from .models import BudgetItem, WishListItem


class ModelAdminWithoutUserExtras(admin.ModelAdmin):

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if user := form.base_fields.get('user'):
            user.widget.can_add_related = False
            user.widget.can_change_related = False
            user.widget.can_delete_related = False
            user.widget.can_view_related = False

        return form


@admin.register(BudgetItem)
class BudgetItemModelAdmin(ModelAdminWithoutUserExtras):
    fieldsets = [
        (
            'Item Info', {
                'fields': ['name', 'narration', 'tags', 'user']
            }
        ),
        (
            'Item details', {
                'fields': ['amount', 'start_date', 'end_date', 'date_added', 'date_modified']
            }
        )
    ]
    readonly_fields = ['date_added', 'date_modified']
    list_filter = ['tags']
    search_fields = ['name']
    list_display = ['name', 'start_date', 'end_date', 'amount', 'user']
    actions = None


@admin.register(WishListItem)
class WishListItemModelAdmin(ModelAdminWithoutUserExtras):
    fieldsets = [
        (
            'Item Info', {
                'fields': ['name', 'narration', 'user', 'granted']
            }
        ),
        (
            'Item details', {
                'fields': ['price', 'due_date', 'date_added', 'date_modified']
            }
        )
    ]
    readonly_fields = ['date_added', 'date_modified']
    search_fields = ['name']
    list_display = ['name', 'due_date', 'price', 'user', 'granted']
    actions = None
