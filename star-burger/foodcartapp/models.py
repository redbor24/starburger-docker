from collections import defaultdict

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Sum
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

# from .geotools import get_locations, get_distance
from star_burger.settings import GEO_ENGINE_BASE_URL
import requests
from django.conf import settings
from geopy import distance


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


def order_mum_default():
    return '1'


class OrderQuerySet(models.QuerySet):
    def get_order_amount(self):
        return self.annotate(amount=Sum(F('lines__quantity') * F('lines__price')))

    def get_restaurants_for_orders(self):
        """
        Возвращает для каждого заказа список ресторанов, которые могут его приготовить
        """
        menu_items = RestaurantMenuItem.objects.select_related('restaurant', 'product')

        orders_addresses = [order.delivery_address for order in self]
        restaurants_addresses = list(set([restaurant.restaurant.address for restaurant in menu_items]))
        locations = get_locations(*orders_addresses, *restaurants_addresses)

        products_in_restaurants = defaultdict(list)
        for menu_item in menu_items:
            products_in_restaurants[menu_item.product].append(menu_item.restaurant)

        for order in self:
            order_products = list()
            products = order.lines.all()
            for product in products:
                order_products.append(products_in_restaurants[product.product])

            restaurants_for_order = set.intersection(*map(set, order_products))
            order.restaurants = restaurants_for_order
            get_distance(order, locations)

        return self


class Order(models.Model):
    ORDER_STATUS = (
        ('u', 'Необработанный'),
        ('p', 'Обработанный'),
        ('i', 'Готовится'),
    )
    PAYMENT_TYPE = (
        ('cashless', 'По карте при оформлении'),
        ('cash', 'Наличными при доставке'),
    )
    order_num = models.CharField(max_length=255, verbose_name='Номер заказа', default=order_mum_default)
    first_name = models.CharField(max_length=255, verbose_name='Имя заказчика', db_index=True)
    last_name = models.CharField(max_length=255, verbose_name='Фамилия заказчика', db_index=True)
    phone_number = PhoneNumberField(verbose_name='Телефон', db_index=True)
    delivery_address = models.TextField(verbose_name='Адрес заказа')
    created_at = models.DateTimeField(verbose_name='Дата и время создания заказа', default=timezone.now, db_index=True)
    status = models.CharField(verbose_name='Статус', max_length=1, choices=ORDER_STATUS, default='u', db_index=True)
    comment = models.TextField(verbose_name='Комментарий к заказу', blank=True)
    called_at = models.DateTimeField(verbose_name='Дата звонка', blank=True, null=True, db_index=True)
    delivered_at = models.DateTimeField(verbose_name='Дата доставки', blank=True, null=True, db_index=True)
    payment_type = models.CharField(verbose_name='Тип оплаты', max_length=12, choices=PAYMENT_TYPE,
                                    default='cashless', db_index=True)
    restaurant = models.ForeignKey(Restaurant, verbose_name='Ресторан', related_name='restorans',
                                   on_delete=models.CASCADE, null=True, blank=True)

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f"{self.id}, {self.last_name} {self.first_name}, {self.phone_number}, {self.delivery_address}"

    @classmethod
    def get_new_order_num(cls):
        return Order.objects.count() + 1


class OrderLines(models.Model):
    order = models.ForeignKey(Order, verbose_name='Заказ', related_name='lines', db_index=True,
                              on_delete=models.CASCADE)
    position_num = models.IntegerField(verbose_name='Номер позиции', default=1)
    product = models.ForeignKey(Product, verbose_name='Позиция', related_name='order_lines', db_index=True,
                                on_delete=models.CASCADE)
    quantity = models.IntegerField(verbose_name='Количество, шт.', default=1,
                                   validators=[MinValueValidator(1)])
    price = models.DecimalField(verbose_name='Цена', max_digits=8, decimal_places=2, default=0,
                                validators=[MinValueValidator(1, 'Цена должна быть больше 0')])

    class Meta:
        verbose_name = 'Позиции заказа'
        verbose_name_plural = 'Позиции заказов'

    def __str__(self):
        return f"заказ: {self.order.order_num}, №{self.position_num}, {self.product}, кол-во: {self.quantity}"


class Location(models.Model):
    address = models.CharField(verbose_name='Адрес', max_length=100, db_index=True, unique=True)
    lat = models.FloatField('Широта', db_index=True, blank=True)
    lon = models.FloatField('Долгота', db_index=True, blank=True)
    creation_date = models.DateField(verbose_name='Дата добавления записи', default=timezone.now, db_index=True)

    class Meta:
        verbose_name = 'Координаты заказа'
        verbose_name_plural = 'Координаты заказов'

    def __str__(self):
        return self.address


def fetch_coordinates(address):
    response = requests.get(GEO_ENGINE_BASE_URL, params={
        'geocode': address,
        'apikey': settings.YANDEX_GEOCODER_API,
        'format': 'json',
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(' ')
    return lat, lon


def get_distance(order, locations):
    order_coordinates = locations.get(order.delivery_address)
    for restaurant in order.restaurants:
        restaurant_coordinates = locations.get(restaurant.address)
        if order_coordinates and restaurant_coordinates:
            restaurant.distance_for_order = round(distance.distance(order_coordinates, restaurant_coordinates).km, 3)
        else:
            restaurant.distance_for_order = 10.0
    return order


def get_locations(*addresses):
    locations = {
        location.address: (location.lat, location.lon)
        for location in Location.objects.filter(address__in=addresses)
    }
    new_locations = list()
    for address in addresses:
        if address in locations.keys():
            continue
        coordinates = fetch_coordinates(address)
        if coordinates:
            lat, lon = coordinates
            location = Location(address=address, lat=lat, lon=lon)
            locations[location.address] = (location.lat, location.lon,)
            new_locations.append(location)
    Location.objects.bulk_create(new_locations)
    return locations
