from django.db import models
from django.utils import timezone


class Location(models.Model):
    address = models.CharField(max_length=100, verbose_name='Адрес', db_index=True, unique=True)
    lat = models.FloatField('Широта', db_index=True, null=True)
    lon = models.FloatField('Долгота', db_index=True, null=True)
    creation_date = models.DateField(verbose_name='Дата добавления записи', default=timezone.now, db_index=True)

    class Meta:
        verbose_name = 'Координаты заказа'
        verbose_name_plural = 'Координаты заказов'

    def __str__(self):
        return self.address


