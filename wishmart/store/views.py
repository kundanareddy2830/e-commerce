from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse, Http404
from .models import Product, Order, OrderItem, Category, ProductReview
from .cart import Cart
from .notifications import send_order_confirmation_email, send_welcome_email
from .payments import process_payment
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django import forms
from django.utils import timezone
from django.db import models
from django.core.paginator import Paginator
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

# Create your views here.

def home(request):
    """Home page view"""
    try:
        featured_products = Product.objects.filter(available=True)[:6]
        categories = Category.objects.all()[:4]
        return render(request, 'store/home.html', {
            'now': timezone.now(),
            'featured_products': featured_products,
            'categories': categories
        })
    except Exception as e:
        logger.error(f"Error in home view: {e}")
        messages.error(request, "An error occurred while loading the home page.")
        return render(request, 'store/home.html', {'now': timezone.now()})

def product_list(request):
    """Product list view with search and pagination"""
    try:
        query = request.GET.get('q', '')
        category_filter = request.GET.get('category', '')
        sort_by = request.GET.get('sort', 'name')
        
        products = Product.objects.filter(available=True)
        
        # Apply search filter
        if query:
            products = products.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
        
        # Apply category filter
        if category_filter:
            products = products.filter(category__slug=category_filter)
        
        # Apply sorting
        if sort_by == 'price_low':
            products = products.order_by('price')
        elif sort_by == 'price_high':
            products = products.order_by('-price')
        elif sort_by == 'newest':
            products = products.order_by('-created')
        else:
            products = products.order_by('name')
        
        # Pagination
        paginator = Paginator(products, 12)  # 12 products per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        categories = Category.objects.all()
        
        return render(request, 'store/product_list.html', {
            'products': page_obj,
            'categories': categories,
            'now': timezone.now(),
            'query': query,
            'sort_by': sort_by,
            'category_filter': category_filter
        })
    except Exception as e:
        logger.error(f"Error in product_list view: {e}")
        messages.error(request, "An error occurred while loading products.")
        return render(request, 'store/product_list.html', {
            'products': [],
            'categories': [],
            'now': timezone.now()
        })

def product_list_by_category(request, category_slug):
    """Product list filtered by category"""
    try:
        category = get_object_or_404(Category, slug=category_slug)
        query = request.GET.get('q', '')
        sort_by = request.GET.get('sort', 'name')
        
        products = Product.objects.filter(category=category, available=True)
        
        if query:
            products = products.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
        
        # Apply sorting
        if sort_by == 'price_low':
            products = products.order_by('price')
        elif sort_by == 'price_high':
            products = products.order_by('-price')
        elif sort_by == 'newest':
            products = products.order_by('-created')
        else:
            products = products.order_by('name')
        
        # Pagination
        paginator = Paginator(products, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        categories = Category.objects.all()
        
        return render(request, 'store/product_list.html', {
            'products': page_obj,
            'categories': categories,
            'selected_category': category,
            'now': timezone.now(),
            'query': query,
            'sort_by': sort_by
        })
    except Http404:
        messages.error(request, "Category not found.")
        return redirect('product_list')
    except Exception as e:
        logger.error(f"Error in product_list_by_category view: {e}")
        messages.error(request, "An error occurred while loading products.")
        return redirect('product_list')

def product_detail(request, id, slug):
    """Product detail view with reviews"""
    try:
        product = get_object_or_404(Product, id=id, slug=slug, available=True)
        reviews = product.reviews.select_related('user').all()
        avg_rating = reviews.aggregate(models.Avg('rating'))['rating__avg']
        review_submitted = False
        
        if request.user.is_authenticated:
            if request.method == 'POST' and 'review_submit' in request.POST:
                try:
                    rating = int(request.POST.get('rating', 5))
                    comment = request.POST.get('comment', '')
                    
                    if 1 <= rating <= 5:
                        ProductReview.objects.update_or_create(
                            product=product, user=request.user,
                            defaults={'rating': rating, 'comment': comment}
                        )
                        review_submitted = True
                        messages.success(request, "Thank you for your review!")
                        
                        # Refresh reviews and average rating
                        reviews = product.reviews.select_related('user').all()
                        avg_rating = reviews.aggregate(models.Avg('rating'))['rating__avg']
                    else:
                        messages.error(request, "Rating must be between 1 and 5.")
                except ValueError:
                    messages.error(request, "Invalid rating value.")
                except Exception as e:
                    logger.error(f"Error submitting review: {e}")
                    messages.error(request, "An error occurred while submitting your review.")
        
        return render(request, 'store/product_detail.html', {
            'product': product,
            'now': timezone.now(),
            'reviews': reviews,
            'avg_rating': avg_rating,
            'review_submitted': review_submitted
        })
    except Http404:
        messages.error(request, "Product not found.")
        return redirect('product_list')
    except Exception as e:
        logger.error(f"Error in product_detail view: {e}")
        messages.error(request, "An error occurred while loading the product.")
        return redirect('product_list')

@require_POST
def add_to_cart(request, product_id):
    """Add product to cart"""
    try:
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id, available=True)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            messages.error(request, "Quantity must be greater than 0.")
            return redirect('product_detail', id=product_id, slug=product.slug)
        
        if quantity > product.stock:
            messages.error(request, f"Only {product.stock} items available in stock.")
            return redirect('product_detail', id=product_id, slug=product.slug)
        
        cart.add(product=product, quantity=quantity, update_quantity=False)
        request.session['show_added_to_cart_toast'] = True
        messages.success(request, f"{product.name} added to cart!")
        
        return redirect('cart_detail')
    except ValueError:
        messages.error(request, "Invalid quantity.")
        return redirect('product_detail', id=product_id, slug=product.slug)
    except Exception as e:
        logger.error(f"Error adding to cart: {e}")
        messages.error(request, "An error occurred while adding to cart.")
        return redirect('product_list')

@require_POST
def remove_from_cart(request, product_id):
    """Remove product from cart"""
    try:
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id, available=True)
        cart.remove(product)
        messages.success(request, f"{product.name} removed from cart.")
        return redirect('cart_detail')
    except Exception as e:
        logger.error(f"Error removing from cart: {e}")
        messages.error(request, "An error occurred while removing from cart.")
        return redirect('cart_detail')

def cart_detail(request):
    """Cart detail view"""
    try:
        cart = Cart(request)
        show_toast = request.session.pop('show_added_to_cart_toast', False)
        return render(request, 'store/cart_detail.html', {
            'cart': cart,
            'now': timezone.now(),
            'show_toast': show_toast
        })
    except Exception as e:
        logger.error(f"Error in cart_detail view: {e}")
        messages.error(request, "An error occurred while loading your cart.")
        return render(request, 'store/cart_detail.html', {
            'cart': Cart(request),
            'now': timezone.now()
        })

class CheckoutForm(forms.ModelForm):
    """Checkout form with validation"""
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address', 'postal_code', 'city']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
        }

@login_required
def checkout(request):
    """Checkout view with payment processing"""
    try:
        cart = Cart(request)
        if len(cart) == 0:
            messages.warning(request, "Your cart is empty.")
            return redirect('cart_detail')
        
        if request.method == 'POST':
            form = CheckoutForm(request.POST)
            if form.is_valid():
                try:
                    order = form.save(commit=False)
                    order.user = request.user
                    order.save()
                    
                    # Create order items
                    for item in cart:
                        OrderItem.objects.create(
                            order=order,
                            product=item['product'],
                            price=item['price'],
                            quantity=item['quantity']
                        )
                    
                    # Clear cart
                    cart.clear()
                    
                    # Send confirmation email (optional - won't break if it fails)
                    try:
                        send_order_confirmation_email(order)
                    except Exception as e:
                        logger.error(f"Failed to send order confirmation email: {e}")
                        # Don't fail the order if email fails
                    
                    messages.success(request, f"Order placed successfully!")
                    
                    # Render the order completion page
                    return render(request, 'store/order_complete.html', {
                        'order': order,
                        'now': timezone.now()
                    })
                    
                except Exception as e:
                    logger.error(f"Error creating order: {e}")
                    messages.error(request, f"An error occurred while processing your order: {str(e)}")
                    return render(request, 'store/checkout.html', {
                        'cart': cart,
                        'form': form,
                        'now': timezone.now()
                    })
            else:
                # Form is invalid
                messages.error(request, "Please correct the errors below.")
                return render(request, 'store/checkout.html', {
                    'cart': cart,
                    'form': form,
                    'now': timezone.now()
                })
        else:
            form = CheckoutForm()
        
        return render(request, 'store/checkout.html', {
            'cart': cart,
            'form': form,
            'now': timezone.now()
        })
    except Exception as e:
        logger.error(f"Error in checkout view: {e}")
        messages.error(request, f"An error occurred during checkout: {str(e)}")
        return redirect('cart_detail')

def register(request):
    """User registration view"""
    try:
        if request.method == 'POST':
            form = UserCreationForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                
                # Send welcome email
                try:
                    send_welcome_email(user)
                except Exception as e:
                    logger.error(f"Failed to send welcome email: {e}")
                
                messages.success(request, "Registration successful! Welcome to our store!")
                return redirect('product_list')
        else:
            form = UserCreationForm()
        
        return render(request, 'store/register.html', {
            'form': form,
            'now': timezone.now()
        })
    except Exception as e:
        logger.error(f"Error in register view: {e}")
        messages.error(request, "An error occurred during registration.")
        return render(request, 'store/register.html', {
            'form': UserCreationForm(),
            'now': timezone.now()
        })

def user_login(request):
    """User login view"""
    try:
        if request.method == 'POST':
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('product_list')
        else:
            form = AuthenticationForm()
        
        return render(request, 'store/login.html', {
            'form': form,
            'now': timezone.now()
        })
    except Exception as e:
        logger.error(f"Error in user_login view: {e}")
        messages.error(request, "An error occurred during login.")
        return render(request, 'store/login.html', {
            'form': AuthenticationForm(),
            'now': timezone.now()
        })

def user_logout(request):
    """User logout view"""
    try:
        logout(request)
        messages.success(request, "You have been logged out successfully.")
        return redirect('product_list')
    except Exception as e:
        logger.error(f"Error in user_logout view: {e}")
        return redirect('product_list')

@login_required
def order_history(request):
    """Order history view"""
    try:
        orders = Order.objects.filter(user=request.user).order_by('-created')
        return render(request, 'store/order_history.html', {
            'orders': orders,
            'now': timezone.now()
        })
    except Exception as e:
        logger.error(f"Error in order_history view: {e}")
        messages.error(request, "An error occurred while loading your order history.")
        return render(request, 'store/order_history.html', {
            'orders': [],
            'now': timezone.now()
        })

@login_required
def order_detail(request, order_id):
    """Order detail view"""
    try:
        order = get_object_or_404(Order, id=order_id, user=request.user)
        return render(request, 'store/order_detail.html', {
            'order': order,
            'now': timezone.now()
        })
    except Http404:
        messages.error(request, "Order not found.")
        return redirect('order_history')
    except Exception as e:
        logger.error(f"Error in order_detail view: {e}")
        messages.error(request, "An error occurred while loading the order.")
        return redirect('order_history')
