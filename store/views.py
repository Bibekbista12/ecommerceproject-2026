from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Product, Order, OrderItem, Category
from .forms import RegisterForm

# Home
def home(request):
    products = Product.objects.filter(stock__gt=0)
    categories = Category.objects.all()
    return render(request, 'store/home.html', {
        'products': products,
        'categories': categories
    })

# Product detail
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product.html', {'product': product})

# Add to cart
@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    order, created = Order.objects.get_or_create(
        user=request.user, is_complete=False
    )
    item, created = OrderItem.objects.get_or_create(
        order=order, product=product
    )
    if not created:
        item.quantity += 1
        item.save()
    messages.success(request, f'{product.name} added to cart!')
    return redirect('cart')

# Cart
@login_required
def cart(request):
    order, created = Order.objects.get_or_create(
        user=request.user, is_complete=False
    )
    items = order.orderitem_set.all()
    total = sum(item.get_total() for item in items)
    return render(request, 'store/cart.html', {
        'items': items,
        'total': total
    })

# Checkout
@login_required
def checkout(request):
    order = Order.objects.get(user=request.user, is_complete=False)
    order.is_complete = True
    order.save()
    messages.success(request, 'Order placed successfully!')
    return render(request, 'store/checkout_success.html')

# Register
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.username}! Account created successfully.')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'store/register.html', {'form': form})

# Login
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password!')
    return render(request, 'store/login.html')

# Logout
def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')