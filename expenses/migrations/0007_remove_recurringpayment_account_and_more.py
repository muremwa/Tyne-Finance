# Generated by Django 4.2.1 on 2023-06-30 12:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('expenses', '0006_recurringpayment_renewal_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recurringpayment',
            name='account',
        ),
        migrations.AddField(
            model_name='recurringpayment',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
