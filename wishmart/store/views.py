from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Order, OrderItem, Category, ProductReview
from .cart import Cart
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django import forms
from django.utils import timezone
from django.db import models

# Create your views here.

def home(request):
    return render(request, 'store/home.html', {'now': timezone.now()})

def product_list(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(available=True)
    if query:
        products = products.filter(
            models.Q(name__icontains=query) | models.Q(description__icontains=query)
        )
    categories = Category.objects.all()
    return render(request, 'store/product_list.html', {'products': products, 'categories': categories, 'now': timezone.now(), 'query': query})

def product_list_by_category(request, category_slug):
    query = request.GET.get('q', '')
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category, available=True)
    if query:
        products = products.filter(
            models.Q(name__icontains=query) | models.Q(description__icontains=query)
        )
    categories = Category.objects.all()
    return render(request, 'store/product_list.html', {'products': products, 'categories': categories, 'selected_category': category, 'now': timezone.now(), 'query': query})

def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    reviews = product.reviews.select_related('user').all()
    avg_rating = reviews.aggregate(models.Avg('rating'))['rating__avg']
    review_submitted = False
    if request.user.is_authenticated:
        if request.method == 'POST' and 'review_submit' in request.POST:
            rating = int(request.POST.get('rating', 5))
            comment = request.POST.get('comment', '')
            ProductReview.objects.update_or_create(
                product=product, user=request.user,
                defaults={'rating': rating, 'comment': comment}
            )
            review_submitted = True
            reviews = product.reviews.select_related('user').all()
            avg_rating = reviews.aggregate(models.Avg('rating'))['rating__avg']
    return render(request, 'store/product_detail.html', {
        'product': product,
        'now': timezone.now(),
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_submitted': review_submitted
    })

@require_POST
def add_to_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, available=True)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product=product, quantity=quantity, update_quantity=False)
    request.session['show_added_to_cart_toast'] = True
    return redirect('cart_detail')

@require_POST
def remove_from_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, available=True)
    cart.remove(product)
    return redirect('cart_detail')

def cart_detail(request):
    cart = Cart(request)
    show_toast = request.session.pop('show_added_to_cart_toast', False)
    return render(request, 'store/cart_detail.html', {'cart': cart, 'now': timezone.now(), 'show_toast': show_toast})

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address', 'postal_code', 'city']

@login_required
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect('cart_detail')
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.paid = True  # For demo, mark as paid
            order.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            cart.clear()
            return render(request, 'store/order_complete.html', {'order': order, 'now': timezone.now()})
    else:
        form = CheckoutForm()
    return render(request, 'store/checkout.html', {'cart': cart, 'form': form, 'now': timezone.now()})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('product_list')
    else:
        form = UserCreationForm()
    return render(request, 'store/register.html', {'form': form, 'now': timezone.now()})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('product_list')
    else:
        form = AuthenticationForm()
    return render(request, 'store/login.html', {'form': form, 'now': timezone.now()})

def user_logout(request):
    logout(request)
    return redirect('product_list')

def order_complete(request, order):
    return render(request, 'store/order_complete.html', {'order': order, 'now': timezone.now()})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'store/order_history.html', {'orders': orders, 'now': timezone.now()})
