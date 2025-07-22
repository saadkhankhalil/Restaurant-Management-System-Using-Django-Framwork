from django.shortcuts import render
from .models import *
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone
from django.http import HttpResponse
from .utils import render_to_pdf
from django.core.paginator import Paginator
from django.db.models import Count, Sum
from django.utils.timezone import now, timedelta
from django.shortcuts import render
from .models import Category, Product, Sale
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.db import connection
from django.db.models import Q

# Create your views here.
def adminHome(request):
    return render(request, 'admin_base.html')

#Add Category
def add_category(request):
    if request.method == "POST":
        name = request.POST['name']
        Category.objects.create(name=name)
        msg = "Category added"
    return render(request, 'add_category.html', locals())

#View Category
def view_category(request):
    category = Category.objects.all()
    return render(request, 'view_category.html', locals())

#Update Category
def edit_category(request, pid):
    category = Category.objects.get(id=pid)
    if request.method == "POST":
        name = request.POST['name']
        category.name = name
        category.save()
        messages.success(request, "Category Updated")
        return redirect('view_category')
    return render(request, 'edit_category.html', locals())
#Delete Category
def delete_category(request, pid):
    category = Category.objects.get(id=pid)
    category.delete()
    messages.success(request, "Category Deleted")
    return redirect('view_category')
#Add Product
def add_product(request):
    category = Category.objects.all()
    if request.method == "POST":
        name = request.POST['name']
        price = request.POST['price']
        image = request.FILES['image']
        cat_id = request.POST['category']
        category = Category.objects.get(id=cat_id)
        Product.objects.create(category=category, name=name, price=price, image=image)
        messages.success(request, "Product added")
        return redirect('view_product')
    return render(request, 'add_product.html', locals())
#View Product
def view_product(request):
    all_products = Product.objects.all().order_by('-id')  # Optional: newest first
    paginator = Paginator(all_products, 5)  # Show 5 products per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'view_product.html', {'product': page_obj})

#Update Product
def edit_product(request, pid):
    product = Product.objects.get(id=pid)
    category = Category.objects.all()
    if request.method == "POST":
        name = request.POST['name']
        price = request.POST['price']
        image = request.FILES.get('image', product.image)  # Use existing image if not updated
        cat_id = request.POST['category']
        category = Category.objects.get(id=cat_id)
        product.category = category
        product.name = name
        product.price = price
        product.image = image
        product.save()
        messages.success(request, "Product Updated")
        return redirect('view_product')
    return render(request, 'edit_product.html', locals())
#Delete Product
def delete_product(request, pid):
    product = Product.objects.get(id=pid)
    product.delete()
    messages.success(request, "Product Deleted")
    return redirect('view_product')
#############################POS functionality can be added here later############################################

def pos(request):
    # Get or initialize session cart
    if 'cart' not in request.session:
        request.session['cart'] = []

    session_cart = request.session['cart']
    cart = []

    # Populate cart from session
    for item in session_cart:
        try:
            product = Product.objects.get(id=item['product_id'])
            cart.append({
                'product': product,
                'qty': item['qty'],
                'total': product.price * item['qty']
            })
        except Product.DoesNotExist:
            continue

    # Filter products
    category_id = request.GET.get('category')
    if category_id:
        products = Product.objects.filter(category_id=category_id)
    else:
        products = Product.objects.all()

    categories = Category.objects.all()

    if request.method == 'POST':
        product_id = request.POST.get('add_to_cart')
        if product_id:
            product = Product.objects.get(id=product_id)
            found = False
            for item in session_cart:
                if item['product_id'] == int(product_id):
                    item['qty'] += 1
                    found = True
                    break
            if not found:
                session_cart.append({'product_id': int(product_id), 'qty': 1})
            request.session['cart'] = session_cart
            return redirect('pos')

    # Total price calculation
    total_price = sum(item['total'] for item in cart)

    return render(request, 'pos.html', {
        'categories': categories,
        'products': products,
        'cart': cart,
        'total_price': total_price,
    })

def clear_cart(request):
    request.session['cart'] = []
    return redirect('pos')





import json  # Replace eval for safety

from decimal import Decimal  # Add this import at the top

def checkout_view(request):
    if request.method == 'POST':
        customer = request.POST.get('customer_name')
        phone = request.POST.get('phone_no')
        discount = request.POST.get('discount') or 0
        service = request.POST.get('service_charges') or 0
        amount = request.POST.get('amount') or 0
        received = request.POST.get('received') or 0
        payment = request.POST.get('payment_method')
        items = request.POST.get('items')

        # Convert string to decimal
        discount = float(discount)
        service = float(service)
        amount = float(amount)

        if 'pending' in request.POST:
            pending = PendingSale.objects.create(
                customer_name=customer,
                phone_no=phone,
                amount=amount,
                tax=0,  # If tax logic exists, add it here
                discount=discount,
                service_charges=service,
                payment_method=payment
            )

            if items:
                items_data = json.loads(items)
                for i, item in enumerate(items_data, start=1):
                    PendingSaleDetail.objects.create(
                        pending_sale=pending,
                        sr_no=i,
                        p_name=item['name'],
                        p_qty=item['qty'],
                        p_price=item['price'],
                        p_amount=item['qty'] * item['price']
                    )

            messages.success(request, "Order saved as pending.")
            return redirect('pending_sales')  # Make sure this URL is set

        # You can handle the normal "checkout" flow here...

    # Default response
    return render(request, 'checkout.html', {'cart_total': 0})  # replace 0 with real total if needed

def show_receipt(request, sale_id):
    from .models import Sale
    try:
        sale = Sale.objects.get(pk=sale_id)
        return render(request, "receipt.html", {"sale": sale})
    except Sale.DoesNotExist:
        return HttpResponse("Receipt not found")
    
#Dashboard
def dashboard_view(request):
    today = now().date()
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    start_of_month = today.replace(day=1)

    # Optional filters from GET parameters
    filter_by = request.GET.get("filter", "daily")  # daily, weekly, monthly

    if filter_by == "daily":
        sales = Sale.objects.filter(date__date=today)
        period_label = "Today"
    elif filter_by == "weekly":
        sales = Sale.objects.filter(date__date__gte=start_of_week)
        period_label = "This Week"
    elif filter_by == "monthly":
        sales = Sale.objects.filter(date__date__gte=start_of_month)
        period_label = "This Month"
    else:
        sales = Sale.objects.all()
        period_label = "All Time"

    # Aggregated values
    total_categories = Category.objects.count()
    total_products = Product.objects.count()
    total_sales_count = sales.count()
    total_sales_amount = sales.aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'total_categories': total_categories,
        'total_products': total_products,
        'total_sales_count': total_sales_count,
        'total_sales_amount': total_sales_amount,
        'period_label': period_label,
        'selected_filter': filter_by,
    }

    return render(request, 'dashboard.html', context)

#Add Expense
def add_expense(request):
    msg = ""
    if request.method == "POST":
        title = request.POST.get('title')
        amount = request.POST.get('amount')
        expense_date = request.POST.get('expense_date')

        if title and amount and expense_date:
            Expense.objects.create(
                title=title,
                amount=amount,
                expense_date=expense_date
            )
            msg = "Expense added successfully."
        else:
            msg = "Please fill all required fields."

    return render(request, 'expense.html', locals())
#view Expense
def view_expenses(request):
    expenses = Expense.objects.all().order_by('-expense_date')
    return render(request, 'view_expense.html', locals())
#Edit Delete Expense
def edit_expense(request, id):
    expense = get_object_or_404(Expense, pk=id)
    msg = ""

    if request.method == "POST":
        title = request.POST.get('title')
        amount = request.POST.get('amount')
        expense_date = request.POST.get('expense_date')

        if title and amount and expense_date:
            expense.title = title
            expense.amount = amount
            expense.expense_date = expense_date
            expense.save()
            msg = "Expense updated successfully."
        else:
            msg = "All fields are required."

    return render(request, 'edit_expense.html', locals())
#Delete Expense

def delete_expense(request, id):
    expense = get_object_or_404(Expense, pk=id)
    expense.delete()
    return redirect('view_expenses') 

# Check Transaction Details
def check_transaction(request):
    transactions = None
    searched = False
    transaction_id = request.GET.get('transaction_id')

    if transaction_id:
        searched = True
        transactions = Sale.objects.filter(id=transaction_id)

    return render(request, 'check_transaction.html', {
        'transactions': transactions,
        'searched': searched
    })


def check_all_transactions(request):
    transactions = Sale.objects.all().order_by('-date')
    return render(request, 'check_transaction.html', {
        'transactions': transactions,
        'searched': True
    })


def check_daily_transactions(request):
    today = now().date()
    transactions = Sale.objects.filter(date__date=today)
    return render(request, 'check_transaction.html', {
        'transactions': transactions,
        'searched': True
    })


def delete_transaction(request, id):
    transaction = get_object_or_404(Sale, id=id)
    transaction.delete()
    return redirect('check_transaction')

# Pending Sales

def pending_sales(request):
    query = request.GET.get('q', '')
    if query:
        sales = PendingSale.objects.filter(customer_name__icontains=query) | PendingSale.objects.filter(phone_no__icontains=query)
    else:
        sales = PendingSale.objects.all().order_by('-date')
    return render(request, 'pending_sales.html', {'sales': sales})


def mark_as_paid(request, id):
    pending = get_object_or_404(PendingSale, id=id)
    details = pending.details.all()

    # Create a new Sale
    sale = Sale.objects.create(
        customer_name=pending.customer_name,
        phone_no=pending.phone_no,
        amount=pending.amount,
        received=pending.amount,
        change=0,
        discount=pending.discount,
        service_charges=pending.service_charges,
        payment_method=pending.payment_method,
    )

    for d in details:
        SaleDetail.objects.create(
            sale=sale,
            sr_no=d.sr_no,
            product_name=d.p_name,
            quantity=d.p_qty,
            price=d.p_price,
            amount=d.p_amount,
        )

    # Delete original pending sale
    pending.delete()

    messages.success(request, f'Transaction {sale.id} marked as paid.')
    return redirect('pending_sales')
