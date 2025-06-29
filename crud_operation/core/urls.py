from django.urls import path 
from . import views

urlpatterns = [
    path('',views.base,name='base'),
    path('register',views.register,name='Register'),
    path('login',views.log_in,name='login'),
    path('logout/',views.log_out, name="logout"),
    path('profile/',views.profile,name='profile'),
    path('changepassword/',views.changepassword, name="changepassword"),
    path('stock/', views.stock_page, name='stock_page'),
    path('billing/', views.billing_page, name='billing_page'),
    path('stock/delete/<int:item_id>/', views.delete_stock, name='delete_stock'),
    path('stock/update/<int:item_id>/', views.update_stock, name='update_stock'),
    path('billing/delete/<int:bill_id>/', views.delete_billing, name='delete_billing'),
    path('clear-customer/', views.clear_customer_data, name='clear_customer_data'),





    # path('generate-invoice/', views.generate_invoice, name='generate_invoice'),
    path('invoice/<int:invoice_id>/', views.generate_invoice, name='generate_invoice'),





    path('invoice-history/', views.invoice_history, name='invoice_history'),
    path('finalize-invoice/', views.finalize_invoice, name='finalize_invoice'),









    
    
    
]
