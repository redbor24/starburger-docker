from django.db import transaction
from django.http import JsonResponse
from django.templatetags.static import static
from phonenumbers import is_valid_number, parse
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from .models import Order, OrderLines, Product


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


class OrderLinesSerializer(ModelSerializer):
    class Meta:
        model = OrderLines
        fields = ['product', 'quantity', 'price']


class OrderSerializer(ModelSerializer):
    products = OrderLinesSerializer(many=True, write_only=True)

    firstname = serializers.CharField(source='first_name')
    lastname = serializers.CharField(source='last_name')
    phonenumber = serializers.CharField(source='phone_number')
    address = serializers.CharField(source='delivery_address')

    def validate_phonenumber(self, value):
        if not is_valid_number(parse(value, "E164")):
            raise serializers.ValidationError('Некорректный телефонный номер')
        return value

    def validate_products(self, value):
        if not value:
            raise serializers.ValidationError('Нет позиций заказа')
        return value

    class Meta:
        model = Order
        fields = ['order_num', 'firstname', 'lastname', 'phonenumber', 'address', 'products']


@transaction.atomic
@api_view(['POST'])
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    new_order = Order.objects.create(
        order_num=Order.get_new_order_num(),
        first_name=serializer.validated_data['first_name'],
        last_name=serializer.validated_data['last_name'],
        phone_number=serializer.validated_data['phone_number'],
        delivery_address=serializer.validated_data['delivery_address']
    )

    order_line_fields = serializer.validated_data['products']
    order_lines = [OrderLines(order=new_order, **fields) for fields in order_line_fields]
    OrderLines.objects.bulk_create(order_lines)

    serializer = OrderSerializer(instance=new_order)
    return Response(serializer.data)
