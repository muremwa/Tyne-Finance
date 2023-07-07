# Generated by Django 4.2.1 on 2023-05-26 08:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_account'),
        ('expenses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('planned', models.BooleanField(default=False)),
                ('narration', models.TextField()),
                ('amount', models.IntegerField(default=0)),
                ('transactionCharge', models.IntegerField(default=0)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_occurred', models.DateField()),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='core.account')),
                ('tags', models.ManyToManyField(to='expenses.usagetag')),
            ],
        ),
    ]
