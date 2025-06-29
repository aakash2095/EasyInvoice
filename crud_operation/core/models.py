from django.db import models


# Create your models here.

class Stock(models.Model):
    item_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    

    def __str__(self):
        return f"{self.item_name} ({self.quantity} pcs)"
    
    
class CustomerInvoice(models.Model):
    inv_no = models.CharField(max_length=20,default='TEMP')
    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.customer_name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
class Billing(models.Model):
    invoice = models.ForeignKey(
    'CustomerInvoice',
    on_delete=models.CASCADE,
    related_name='items',
    null=True,
    blank=True
)

    item = models.ForeignKey(Stock, on_delete=models.SET_NULL, null=True, blank=True)
    custom_item_name = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    customer_name = models.CharField(max_length=255,null=True,blank=True)
    customer_phone = models.CharField(max_length=20,null=True,blank=True)
    gst = models.FloatField()
    warranty = models.CharField(
        max_length=100,
        default='No Warranty',
        help_text="Enter warranty period (e.g., 1 Year, 6 Months)"
    )
    payment_mode = models.CharField(
        max_length=50,
        choices=[
            ('Cash', 'Cash'),
            ('Card', 'Card'),
            ('UPI', 'UPI'),
            ('Bank Transfer', 'Bank Transfer'),
        ],
        default='Cash'
    )

    


    def __str__(self):
        if self.item:
            return f"{self.item.item_name} - {self.quantity} pcs @ ₹{self.price}"
        return f"{self.custom_item_name} - {self.quantity} pcs @ ₹{self.price}"


