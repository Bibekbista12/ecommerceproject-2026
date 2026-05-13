from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from .models import Product, Order, OrderItem, Category
from .forms import RegisterForm


# ── Helper: get cart item count for the logged-in user ──────────────────────
def get_cart_count(request):
    if request.user.is_authenticated:
        order = Order.objects.filter(
            user=request.user, is_complete=False
        ).first()
        if order:
            return order.orderitem_set.count()
    return 0


# ── Home ─────────────────────────────────────────────────────────────────────
def home(request):
    featured_products = Product.objects.filter(stock__gt=0)[:8]
    categories = Category.objects.all()[:4]
    return render(request, 'store/home.html', {
        'featured_products': featured_products,
        'categories': categories,
        'cart_count': get_cart_count(request),
    })


# ── Product Detail ───────────────────────────────────────────────────────────
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    related = Product.objects.filter(
        category=product.category, stock__gt=0
    ).exclude(pk=pk)[:4]
    return render(request, 'store/product.html', {
        'product': product,
        'related': related,
        'cart_count': get_cart_count(request),
    })


# ── Add to Cart (supports both regular POST and AJAX fetch) ──────────────────
@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    order, _ = Order.objects.get_or_create(
        user=request.user, is_complete=False
    )
    item, created = OrderItem.objects.get_or_create(
        order=order, product=product
    )
    if not created:
        item.quantity += 1
        item.save()

    cart_count = order.orderitem_set.count()

    # Return JSON if the request came from the Quick Add AJAX fetch
    if request.headers.get('Content-Type') == 'application/json':
        return JsonResponse({
            'success': True,
            'message': f'{product.name} added to cart!',
            'cart_count': cart_count,
        })

    messages.success(request, f'{product.name} added to cart!')
    return redirect('cart')


# ── Remove from Cart ─────────────────────────────────────────────────────────
@login_required
def remove_from_cart(request, pk):
    item = get_object_or_404(OrderItem, pk=pk, order__user=request.user)
    item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('cart')


# ── Cart ─────────────────────────────────────────────────────────────────────
@login_required
def cart(request):
    order, _ = Order.objects.get_or_create(
        user=request.user, is_complete=False
    )
    items = order.orderitem_set.select_related('product').all()
    total = sum(item.get_total() for item in items)
    return render(request, 'store/cart.html', {
        'items': items,
        'total': total,
        'cart_count': items.count(),
    })


# ── Checkout ─────────────────────────────────────────────────────────────────
@login_required
def checkout(request):
    try:
        order = Order.objects.get(user=request.user, is_complete=False)
    except Order.DoesNotExist:
        messages.error(request, 'No active order found.')
        return redirect('cart')

    if request.method == 'POST':
        order.is_complete = True
        order.save()
        messages.success(request, 'Order placed successfully!')
        return render(request, 'store/checkout_success.html', {
            'order': order,
        })

    items = order.orderitem_set.select_related('product').all()
    total = sum(item.get_total() for item in items)
    return render(request, 'store/checkout.html', {
        'order': order,
        'items': items,
        'total': total,
        'cart_count': items.count(),
    })


# ── Register ─────────────────────────────────────────────────────────────────
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request, f'Welcome {user.username}! Account created successfully.'
            )
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'store/register.html', {'form': form})


# ── Login ─────────────────────────────────────────────────────────────────────
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
            messages.error(request, 'Invalid username or password.')
    return render(request, 'store/login.html')


# ── Logout ───────────────────────────────────────────────────────────────────
def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')




def product_list(request):
    category_slug = request.GET.get('category')
    products = Product.objects.filter(stock__gt=0)
    if category_slug:
        products = products.filter(category__slug=category_slug)
    categories = Category.objects.all()
    return render(request, 'store/products.html', {
        'products': products,
        'categories': categories,
        'cart_count': get_cart_count(request),
    })