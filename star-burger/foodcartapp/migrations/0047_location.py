# Generated by Django 3.2 on 2022-09-19 20:58

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0046_auto_20220919_1228'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(db_index=True, max_length=100, unique=True, verbose_name='Адрес')),
                ('lat', models.FloatField(blank=True, db_index=True, verbose_name='Широта')),
                ('lon', models.FloatField(blank=True, db_index=True, verbose_name='Долгота')),
                ('creation_date', models.DateField(db_index=True, default=django.utils.timezone.now, verbose_name='Дата добавления записи')),
            ],
            options={
                'verbose_name': 'Координаты заказа',
                'verbose_name_plural': 'Координаты заказов',
            },
        ),
    ]
