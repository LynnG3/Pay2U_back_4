# Generated by Django 3.2.3 on 2024-04-04 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cashback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=8, verbose_name='Сумма кешбэка')),
            ],
            options={
                'verbose_name': 'Кешбэк',
                'verbose_name_plural': 'Кешбэк',
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total', models.PositiveIntegerField(verbose_name='Общая стоимость')),
                ('accept_rules', models.BooleanField(default=False, verbose_name='Согласие с правилами')),
                ('callback', models.CharField(choices=[('accepted', 'Принят'), ('denied', 'Отклонен')], max_length=10, verbose_name='Ответ от банка')),
                ('payment_date', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата оплаты')),
                ('next_payment_date', models.DateField()),
                ('next_payment_amount', models.PositiveIntegerField()),
            ],
            options={
                'verbose_name': 'Платеж',
                'verbose_name_plural': 'Платежи',
                'ordering': ['-payment_date'],
            },
        ),
        migrations.CreateModel(
            name='TariffKind',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default=None, max_length=50, null=True, verbose_name='Название тарифа')),
                ('duration', models.PositiveIntegerField(choices=[(1, '1 месяц'), (3, '3 месяца'), (6, '6 месяцев'), (12, '12 месяцев')], verbose_name='Длительность подписки в месяцах ')),
                ('cost_per_month', models.IntegerField(default=199, verbose_name='Стоимость в месяц')),
                ('cost_total', models.IntegerField(default=199, verbose_name='Стоимость за период')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание тарифа')),
            ],
            options={
                'verbose_name': 'Тариф',
                'verbose_name_plural': 'Тарифы',
                'ordering': ('-cost_per_month',),
            },
        ),
    ]
