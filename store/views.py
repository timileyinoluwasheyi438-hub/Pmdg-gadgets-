import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Category, Product, Order, OrderItem
from django.shortcuts import render, redirect
from .models import ContactMessage
from django.views.decorators.http import require_POST
from .models import Order, OrderItem, Product
import hmac
import hashlib
from django.conf import settings
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import requests as http



def home(request):
    products = Product.objects.filter(is_active=True).order_by('-is_featured', '-created_at')[:6]
    categories = Category.objects.filter(is_active=True)[:4]
    return render(request, 'store/pages/home.html', {
        'products': products,
        'categories': categories,
    })

def shop(request):
    """All products listing page."""
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)
    return render(request, 'store/pages/shop.html', {
        'products': products,
        'categories': categories,
        'active_category': 'all',
    })


def shop_category(request, category):
    """Filter products by category slug."""
    cat = get_object_or_404(Category, slug=category, is_active=True)
    products = Product.objects.filter(category=cat, is_active=True)
    categories = Category.objects.filter(is_active=True)
    return render(request, 'store/pages/shop.html', {
        'products': products,
        'categories': categories,
        'active_category': category,
        'current_category': cat,
    })


def product_detail(request, slug):
    """Single product page with specs and related products."""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id)[:3]
    return render(request, 'store/pages/product_detail.html', {
        'product': product,
        'related': related,
    })


def cart(request):
    """Shopping cart page."""
    return render(request, 'store/pages/cart.html')


def checkout(request):
    """Multi-step checkout: Contact → Shipping → Review.
    Paystack integration stubbed — uncomment when ready.
    """
    return render(request, 'store/pages/checkout.html')


def services(request):
    """Services page — peripherals, support, software, training."""
    return render(request, 'store/pages/services.html')


def about(request):
    """About PMDG Technology Solution Ltd."""
    return render(request, 'store/pages/about.html')


def faq(request):
    """Frequently Asked Questions."""
    return render(request, 'store/pages/faq.html')


def blog(request):
    """Blog listing page."""
    return render(request, 'store/pages/blog.html')


def handler404(request, exception):
    """Custom 404 page with blue full-bleed design."""
    return render(request, 'store/pages/notfound.html', status=404)


  # add ContactMessage to your existing model import line


def about(request):
    return render(request, 'store/pages/about.html')


def contact(request):
    if request.method == 'POST':
        ContactMessage.objects.create(
            name=request.POST.get('name', '').strip(),
            email=request.POST.get('email', '').strip(),
            subject=request.POST.get('subject', 'other'),
            message=request.POST.get('message', '').strip(),
        )
        return redirect('/about/?sent=1')
    return redirect('/about/')



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm
from .models import Order, Wishlist, Product  # keep your existing model imports alongside these


def register_view(request):
    if request.user.is_authenticated:
        return redirect('account')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('account')
    else:
        form = RegisterForm()
    return render(request, 'store/pages/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('account')
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('account')
        messages.error(request, 'Invalid email or password.')
    return render(request, 'store/pages/login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required(login_url='login')
def account_view(request):
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:3]
    wishlist_count = Wishlist.objects.filter(user=request.user).count()
    return render(request, 'store/pages/account.html', {
        'recent_orders': recent_orders,
        'wishlist_count': wishlist_count,
    })


@login_required(login_url='login')
def order_history_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/pages/order_history.html', {'orders': orders})


@login_required(login_url='login')
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/pages/order_detail.html', {'order': order})


def track_order_view(request):
    order = None
    error = None
    if request.method == 'POST':
        reference = request.POST.get('reference', '').strip().upper()
        email = request.POST.get('email', '').strip().lower()
        order_id_str = reference.replace('PMDG-', '').lstrip('0') or '0'
        try:
            order_id = int(order_id_str)
            order = Order.objects.get(id=order_id, email__iexact=email)
        except (ValueError, Order.DoesNotExist):
            error = "We couldn't find an order with that reference and email. Double-check both and try again."
    return render(request, 'store/pages/track_order.html', {'order': order, 'error': error})


@login_required(login_url='login')
def wishlist_view(request):
    items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'store/pages/wishlist.html', {'items': items})


@login_required(login_url='login')
def wishlist_toggle(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        item.delete()
    return redirect(request.META.get('HTTP_REFERER', 'wishlist'))




# Add to store/views.py

@require_POST
def checkout_submit(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request data.'}, status=400)

    items = data.get('items', [])
    if not items:
        return JsonResponse({'error': 'Your cart is empty.'}, status=400)

    required = ['first_name', 'last_name', 'email', 'street_address', 'city', 'state']
    missing = [f for f in required if not str(data.get(f) or '').strip()]
    if missing:
        return JsonResponse({'error': f"Missing: {', '.join(missing)}"}, status=400)

    subtotal = sum(int(item.get('price') or 0) * int(item.get('qty') or 0) for item in items)
    shipping = 0
    total = subtotal + shipping
    if total < 100:
        return JsonResponse({'error': 'Order total is too small.'}, status=400)

    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        first_name=data['first_name'].strip(),
        last_name=data['last_name'].strip(),
        email=data['email'].strip().lower(),
        phone=data.get('phone', '').strip(),
        street_address=data['street_address'].strip(),
        apartment=data.get('apartment', '').strip(),
        city=data['city'].strip(),
        state=data['state'].strip(),
        postal_code=data.get('postal_code', '').strip(),
        country=data.get('country', 'Nigeria').strip() or 'Nigeria',
        status='pending',
        subtotal=subtotal,
        shipping=shipping,
        total=total,
    )

    for item in items:
        product = Product.objects.filter(id=item.get('id')).first()
        price = int(item.get('price') or (product.price if product else 0))
        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=item.get('name') or (product.name if product else 'Laptop'),
            product_price=price,
            quantity=int(item.get('qty') or 1),
        )

    reference = f"PMDG-{order.id:06d}"
    callback_url = request.build_absolute_uri(f'/paystack/callback/?order_id={order.id}')

    res = http.post(
        'https://api.paystack.co/transaction/initialize',
        headers={
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
            'Content-Type': 'application/json',
        },
        json={
            'email': order.email,
            'amount': int(order.total) * 100,
            'reference': reference,
            'callback_url': callback_url,
            'metadata': {'order_id': order.id},
        },
        timeout=20,
    )
    payload = res.json()
    if not payload.get('status'):
        return JsonResponse({'error': payload.get('message', 'Paystack init failed')}, status=400)

    order.paystack_ref = reference
    order.save(update_fields=['paystack_ref'])

    return JsonResponse({
        'success': True,
        'order_id': order.id,
        'reference': reference,
        'authorization_url': payload['data']['authorization_url'],
    })


def paystack_callback(request):
    reference = request.GET.get('reference', '')
    order_id = request.GET.get('order_id')
    order = get_object_or_404(Order, id=order_id)

    res = http.get(
        f'https://api.paystack.co/transaction/verify/{reference}',
        headers={'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}'},
        timeout=20,
    )
    payload = res.json()
    data = payload.get('data') or {}

    if payload.get('status') and data.get('status') == 'success':
        order.status = 'processing'
        order.paystack_ref = reference
        order.paystack_transaction_id = str(data.get('id', ''))
        order.paid_at = timezone.now()
        order.save()
        return render(request, 'store/pages/payment_success.html', {'order': order})

    return render(request, 'store/pages/payment_failed.html', {'order': order})


@csrf_exempt
@require_POST
def paystack_webhook(request):
    signature = request.META.get('HTTP_X_PAYSTACK_SIGNATURE', '')
    computed = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode(),
        request.body,
        hashlib.sha512,
    ).hexdigest()
    if not hmac.compare_digest(signature, computed):
        return JsonResponse({'error': 'invalid signature'}, status=400)

    event = json.loads(request.body.decode())
    if event.get('event') == 'charge.success':
        data = event.get('data') or {}
        reference = data.get('reference', '')
        order = Order.objects.filter(paystack_ref=reference).first()
        if order and not order.paid_at:
            order.status = 'processing'
            order.paystack_transaction_id = str(data.get('id', ''))
            order.paid_at = timezone.now()
            order.save()
    return JsonResponse({'status': 'ok'})