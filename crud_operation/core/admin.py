from django.contrib import admin
from .models import Stock,Billing

# Register your models here.


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['item_name','quantity']
    search_fields = ['item_name']

@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    list_display = ('item', 'custom_item_name', 'quantity', 'price')
    search_fields = ('item__item_name', 'custom_item_name')
