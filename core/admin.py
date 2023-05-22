from django.contrib import admin

from .models import Currency, User

admin.site.register(Currency)


@admin.register(User)
class UserModelAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None, {
                'fields': ['username', 'currency']
            }
        ),
        (
            'Personal Info', {
                'fields': ['first_name', 'last_name', 'email']
            }
        ),
        (
            'Permissions', {
                'fields': ['is_staff', 'is_superuser', 'is_active', 'groups', 'user_permissions']
            }
        ),
        (
            'Important Dates', {
                'fields': ['date_joined', 'last_login']
            }
        )
    ]
    list_display = ('username', 'email', 'currency', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'currency')
    search_fields = ('username', 'email', 'currency')
    actions = None

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if currency_field := form.base_fields.get('currency'):
            currency_field.widget.can_add_related = False
            currency_field.widget.can_change_related = False
            currency_field.widget.can_delete_related = False
            currency_field.widget.can_view_related = False

        return form
