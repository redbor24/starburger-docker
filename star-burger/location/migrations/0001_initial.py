# Generated by Django 3.2 on 2022-10-05 09:55

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(db_index=True, max_length=100, unique=True, verbose_name='Адрес')),
                ('lat', models.FloatField(db_index=True, null=True, verbose_name='Широта')),
                ('lon', models.FloatField(db_index=True, null=True, verbose_name='Долгота')),
                ('creation_date', models.DateField(db_index=True, default=django.utils.timezone.now, verbose_name='Дата добавления записи')),
            ],
            options={
                'verbose_name': 'Координаты заказа',
                'verbose_name_plural': 'Координаты заказов',
            },
        ),
    ]
