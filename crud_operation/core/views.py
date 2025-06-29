from django.shortcuts import render,redirect
from django.contrib import messages
from django.shortcuts import get_object_or_404

from .forms import Registerform,Authenticateform,changepasswordform
from django.contrib.auth import authenticate, login, logout , update_session_auth_hash
from . models import Stock,Billing,CustomerInvoice
from decimal import Decimal 
from urllib.parse import quote


from django.db.models import Q
















# Create your views here.

def base(request):
    return render (request,'core/base.html')


def register(request):
    if request.method == 'POST':
        rf = Registerform(request.POST)
        if rf.is_valid():
            rf.save()
            messages.success(request, 'Registration successful.')
            return redirect('login')  # or your login/homepage route
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        rf = Registerform()

    return render(request, 'core/Register.html', {'rf': rf})


def log_in(request):
    if request.method == 'POST':
        rf = Authenticateform(request,request.POST)
        if rf.is_valid():
            name = rf.cleaned_data['username']
            pas = rf.cleaned_data['password']
            user = authenticate(username = name , password = pas)
            if user is not None:
                login(request,user)
                return redirect('/')
            else:
                messages.error(request,'not done')
    else:
        rf =  Authenticateform()
    return render (request, 'core/login.html',{'rf':rf})


def log_out(request):
    logout(request)
    return redirect('base')

def profile(request):
    return render(request,'core/profile.html')

def changepassword(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            rf = changepasswordform(request.user,request.POST)
            if rf.is_valid():
                rf.save()
                update_session_auth_hash(request,rf.user)
                return redirect('profile')
        else:
                        rf = changepasswordform(request.user)
        return render(request,'core/changepassword.html',{'rf':rf})
    else:
        return redirect('login')
    

########################################################
def stock_page(request):
    if request.method == 'POST':
        name = request.POST.get('item_name')
        qty = request.POST.get('quantity')

        if name and qty:
            Stock.objects.create(item_name=name, quantity=int(qty))
            messages.success(request, 'Item added successfully!')
        else:
            messages.error(request, 'All fields are required!')

        return redirect('stock_page')

    # 🟡 Handle search query from GET
    query = request.GET.get('search', '')
    if query:
        items = Stock.objects.filter(item_name__icontains=query)
    else:
        items = Stock.objects.all()

    return render(request, 'core/stock.html', {
        'items': items,
        'query': query,
    })


def delete_stock(request, item_id):
    item = get_object_or_404(Stock, id=item_id)
    item.delete()
    messages.success(request, f"Deleted '{item.item_name}' from stock.")
    return redirect('stock_page')


def update_stock(request, item_id):
    item = get_object_or_404(Stock, id=item_id)

    if request.method == 'POST':
        new_name = request.POST.get('item_name')
        new_qty = request.POST.get('quantity')

        if new_name and new_qty:
            item.item_name = new_name
            item.quantity = int(new_qty)
            item.save()
            messages.success(request, 'Item updated successfully!')
            return redirect('stock_page')
        else:
            messages.error(request, 'All fields are required.')
    return render(request, 'core/update_stock.html', {'item': item})


def billing_page(request):
    items = Stock.objects.all()

    if request.method == "POST":
        customer_name = request.POST.get("customer_name") or request.session.get("customer_name")
        customer_phone = request.POST.get("customer_phone") or request.session.get("customer_phone")
        item_id = request.POST.get("item_id")
        custom_name = request.POST.get("custom_name")
        qty = int(request.POST.get("quantity"))
        price = float(request.POST.get("price"))
        gst = request.POST.get("gst")
        warranty = request.POST.get("warranty")
        payment_mode = request.POST.get("payment")  # ✅ Fix name to match HTML input `name="payment"`

        gst = float(gst) if gst else 0

        # Save customer info in session
        if customer_name:
            request.session['customer_name'] = customer_name
        if customer_phone:
            request.session['customer_phone'] = customer_phone

        # Save billing entry
        if item_id:
            item = Stock.objects.get(id=item_id)
            Billing.objects.create(
                item=item,
                quantity=qty,
                price=price,
                customer_name=customer_name,
                customer_phone=customer_phone,
                gst=gst,
                warranty=warranty or '',
                payment_mode=payment_mode or 'Cash'
            )
        elif custom_name:
            Billing.objects.create(
                custom_item_name=custom_name,
                quantity=qty,
                price=price,
                customer_name=customer_name,
                customer_phone=customer_phone,
                gst=gst,
                warranty=warranty or '',
                payment_mode=payment_mode 
            )

        messages.success(request, "Bill item added successfully.")
        return redirect("billing_page")

    # GET request - show billing list
    billings = Billing.objects.filter(invoice__isnull=True)

    subtotal = Decimal('0.00')
    for bill in billings:
        bill.total = Decimal(bill.quantity) * Decimal(bill.price)
        gst_amount = (Decimal(bill.gst) / Decimal('100')) * bill.total
        bill.total += gst_amount
        subtotal += bill.total

    grand_total = subtotal

    last_bill = billings.last() if billings.exists() else None

    context = {
        'items': items,
        'billings': billings,
        'subtotal': subtotal,
        'grand_total': grand_total,
        'request': request,
        'customer_name': request.session.get("customer_name", ""),
        'customer_phone': request.session.get("customer_phone", ""),
        'payment_mode': last_bill.payment_mode if last_bill else '',
        'warranty': last_bill.warranty if last_bill else '', # ✅ Optional, to pass in invoice
    }

    return render(request, 'core/billing.html', context)




def delete_billing(request, bill_id):
    bill = get_object_or_404(Billing, id=bill_id)

    # Optional: Restock if the billed item was from stock
    if bill.item:
        bill.item.quantity += bill.quantity
        bill.item.save()

    bill.delete()
    messages.success(request, 'Billing record deleted successfully.')
    return redirect('billing_page')


def clear_customer_data(request):
    # Clear session
    keys_to_clear = [
        'customer_name', 'customer_phone',
        'custom_item_name', 'item',
        'quantity', 'price', 'gst'
    ]
    for key in keys_to_clear:
        request.session.pop(key, None)

    # Delete existing bills
    Billing.objects.all().delete()  # Optional: filter this for specific users if needed

    messages.success(request, "Customer data and billing records cleared.")
    return redirect('billing_page')

def generate_invoice(request, invoice_id):
    invoice = get_object_or_404(CustomerInvoice, id=invoice_id)

    # Auto-generate invoice number if still TEMP or empty
    if invoice.inv_no == 'TEMP' or not invoice.inv_no:
        invoice.inv_no = f"INVOICE-{invoice.id:03d}"
        invoice.save()

    billings = invoice.items.all()

    subtotal = Decimal('0.00')
    for bill in billings:
        bill.total = Decimal(bill.quantity) * Decimal(bill.price)
        gst_amount = (Decimal(bill.gst) / Decimal('100')) * bill.total
        bill.total += gst_amount
        subtotal += bill.total

    grand_total = subtotal

    # --- WhatsApp Message ---
    message_text = (
        f"Hello {invoice.customer_name},\n\n"
        f"Thank you for shopping with Balaji Computers!\n\n"
        f"Your invoice {invoice.inv_no} dated *{invoice.created_at.strftime('%d %b %Y')}* "
        f"has been successfully generated.\n\n"
        f"Total Amount: ₹{grand_total:.2f}\n\n"
        f"If you need any assistance with your products or services, feel free to reach out to us.\n\n"
        f"Powered by trust, delivered by Balaji Computers.\n\n"
        f"Sunil Soni\n+91 98671 76108"
    )

    encoded_message = quote(message_text)  # properly encode the full message

    whatsapp_url = f"https://wa.me/91{invoice.customer_phone}?text={encoded_message}"

    return render(request, 'core/invoice.html', {
        'billings': billings,
        'grand_total': grand_total,
        'customer_name': invoice.customer_name,
        'customer_phone': invoice.customer_phone,
        'invoice_number': invoice.inv_no,
        'invoice_date': invoice.created_at,
        'whatsapp_url': whatsapp_url,
    })
# def generate_invoice(request, invoice_id):
#     invoice = get_object_or_404(CustomerInvoice, id=invoice_id)

#     # Auto-generate inv_no if still 'TEMP' or empty
#     if invoice.inv_no == 'TEMP' or not invoice.inv_no:
#         invoice.inv_no = f"INVOICE-{invoice.id:03d}"
#         invoice.save()

#     billings = invoice.items.all()

#     subtotal = Decimal('0.00')
#     for bill in billings:
#         bill.total = Decimal(bill.quantity) * Decimal(bill.price)
#         gst_amount = (Decimal(bill.gst) / Decimal('100')) * bill.total
#         bill.total += gst_amount
#         subtotal += bill.total

#     grand_total = subtotal

#     return render(request, 'core/invoice.html', {
#         'billings': billings,
#         'grand_total': grand_total,
#         'customer_name': invoice.customer_name,
#         'customer_phone': invoice.customer_phone,
#         'invoice_number': invoice.inv_no,
#         'invoice_date': invoice.created_at,
#     })


def finalize_invoice(request):
    customer_name = request.session.get('customer_name')
    customer_phone = request.session.get('customer_phone')

    if not customer_name or not customer_phone:
        messages.error(request, "Customer info missing.")
        return redirect('billing_page')

    billings = Billing.objects.filter(
        customer_name=customer_name,
        customer_phone=customer_phone,
        invoice__isnull=True
    )

    if not billings.exists():
        messages.error(request, "No billing items to finalize.")
        return redirect('billing_page')

    total = Decimal('0.00')
    for bill in billings:
        bill_total = Decimal(bill.quantity) * Decimal(bill.price)
        gst_amount = (Decimal(bill.gst) / Decimal('100')) * bill_total
        bill_total += gst_amount
        total += bill_total

    invoice = CustomerInvoice.objects.create(
        customer_name=customer_name,
        customer_phone=customer_phone,
        total_amount=total
    )

    for bill in billings:
        bill.invoice = invoice
        bill.save()

    # Optional: Clear session
    request.session.pop('customer_name', None)
    request.session.pop('customer_phone', None)

    return redirect('generate_invoice', invoice_id=invoice.id)





def invoice_history(request):
    query = request.GET.get('search', '')
    
    if query:
        invoices = CustomerInvoice.objects.filter(
            Q(inv_no__icontains=query) |
            Q(customer_name__icontains=query) |
            Q(customer_phone__icontains=query)
        ).order_by('-created_at')
    else:
        invoices = CustomerInvoice.objects.order_by('-created_at')

    return render(request, 'core/invoice_history.html', {
        'invoices': invoices,
        'query': query,
    })
















############################################

# def generate_invoice(request):
#     customer_name = request.session.get('customer_name')
#     customer_phone = request.session.get('customer_phone')

#     billings = Billing.objects.filter(
#         customer_name=customer_name,
#         customer_phone=customer_phone
#     )

#     subtotal = Decimal('0.00')
#     for bill in billings:
#         bill.total = Decimal(bill.quantity) * Decimal(bill.price)
#         gst_amount = (Decimal(bill.gst) / Decimal('100')) * bill.total
#         bill.total += gst_amount
#         subtotal += bill.total

#     grand_total = subtotal

#     # Prepare WhatsApp message
#     whatsapp_message = f"Invoice for {customer_name}:\nTotal: ₹{grand_total:.2f}"

#     return render(request, 'core/invoice.html', {
#         'billings': billings,
#         'grand_total': grand_total,
#         'customer_name': customer_name,
#         'customer_phone': customer_phone,
#         'whatsapp_message': whatsapp_message,
#     })




# def finalize_invoice(request):
#     customer_name = request.session.get('customer_name')
#     customer_phone = request.session.get('customer_phone')

#     # Get all unlinked billing items for this customer
#     bill_items = Billing.objects.filter(
#         customer_name=customer_name,
#         customer_phone=customer_phone,
#         invoice__isnull=True
#     )

#     if not bill_items.exists():
#         messages.warning(request, "No items found for this customer.")
#         return redirect('billing_page')

#     # Calculate total
#     total = Decimal('0.00')
#     for item in bill_items:
#         subtotal = Decimal(item.quantity) * Decimal(item.price)
#         gst_amount = (Decimal(item.gst) / 100) * subtotal if item.gst else 0
#         total += subtotal + gst_amount

#     # Save invoice
#     invoice = CustomerInvoice.objects.create(
#         customer_name=customer_name,
#         customer_phone=customer_phone,
#         total_amount=total
#     )

#     # Update billing items with this invoice
#     bill_items.update(invoice=invoice)

#     # Clear customer session data so new billing can start fresh
#     request.session.pop('customer_name', None)
#     request.session.pop('customer_phone', None)

#     messages.success(request, f"Invoice created for {customer_name}.")
#     return redirect('billing_page')

#############################################################################################################

# def generate_invoice(request, invoice_id):
#     invoice = get_object_or_404(CustomerInvoice, id=invoice_id)
#     billings = invoice.items.all()

#     subtotal = Decimal('0.00')
#     for bill in billings:
#         bill.total = Decimal(bill.quantity) * Decimal(bill.price)
#         gst_amount = (Decimal(bill.gst) / Decimal('100')) * bill.total
#         bill.total += gst_amount
#         subtotal += bill.total

#     grand_total = subtotal

#     return render(request, 'core/invoice.html', {
#         'billings': billings,
#         'grand_total': grand_total,
#         'customer_name': invoice.customer_name,
#         'customer_phone': invoice.customer_phone,
#     })

######################################################################################################################