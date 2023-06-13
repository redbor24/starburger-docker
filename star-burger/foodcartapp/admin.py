from django.contrib import admin
from django.shortcuts import reverse, redirect
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.http import url_has_allowed_host_and_scheme

from star_burger.settings import ALLOWED_HOSTS

from .models import (Order, OrderLines, Product, ProductCategory, Restaurant,
                     RestaurantMenuItem)


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly, so search will be buggy.
        # Migration to PostgreSQL is necessary
        'name',
        'category__name',
    ]

    inlines = [
        RestaurantMenuItemInline
    ]
    fieldsets = (
        ('Общее', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('Подробно', {
            'fields': [
                'special_status',
                'description',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    save_on_top = True

    class Media:
        css = {
            "all": (
                static("admin/foodcartapp.css")
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html('<img src="{url}" style="max-height: 200px;"/>', url=obj.image.url)
    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html('<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/></a>', edit_url=edit_url, src=obj.image.url)
    get_image_list_preview.short_description = 'превью'


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    pass


class OrderLinesInline(admin.TabularInline):
    model = OrderLines
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_num', 'payment_type', 'status', 'first_name', 'last_name', 'phone_number',
                    'delivery_address', 'created_at']
    fieldsets = (
        (None, {'fields': (('order_num', 'status', 'created_at'),
                           ('payment_type', 'restaurant'),
                           ('first_name', 'last_name', 'phone_number'),
                           ('delivery_address', 'comment'),
                           ('called_at', 'delivered_at')
                           )
                }
         ),
    )
    readonly_fields = ['created_at']
    inlines = [OrderLinesInline]
    save_on_top = True

    def response_change(self, request, obj):
        res = super().response_change(request, obj)
        next = request.GET.get('next')

        if next and url_has_allowed_host_and_scheme(next, ALLOWED_HOSTS):
            return redirect(next)
        else:
            return res

    def save_model(self, request, obj, form, change):
        if obj.restaurant and obj.status == 'u':
            obj.status = 'i'
            obj.save()
        elif not obj.restaurant:
            obj.status = 'u'
            obj.save()
        return super().save_model(request, obj, form, change)


@admin.register(OrderLines)
class OrderLinesAdmin(admin.ModelAdmin):
    pass
