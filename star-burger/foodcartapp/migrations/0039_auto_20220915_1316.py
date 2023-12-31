# Generated by Django 3.2 on 2022-09-15 10:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0038_order_orderlines'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderlines',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lines', to='foodcartapp.order', verbose_name='Заказ'),
        ),
        migrations.AlterField(
            model_name='orderlines',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_lines', to='foodcartapp.product', verbose_name='Позиция'),
        ),
    ]
