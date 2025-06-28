from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Order, OrderItem

def send_order_confirmation_email(order):
    """Send order confirmation email to customer"""
    subject = f'Order Confirmation - Order #{order.id}'
    
    # Get order items for email
    order_items = OrderItem.objects.filter(order=order)
    
    context = {
        'order': order,
        'order_items': order_items,
        'total_cost': order.get_total_cost(),
    }
    
    html_message = render_to_string('store/emails/order_confirmation.html', context)
    plain_message = render_to_string('store/emails/order_confirmation.txt', context)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[order.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send order confirmation email: {e}")
        return False

def send_order_status_update_email(order, status):
    """Send order status update email"""
    subject = f'Order Status Update - Order #{order.id}'
    
    context = {
        'order': order,
        'status': status,
    }
    
    html_message = render_to_string('store/emails/order_status_update.html', context)
    plain_message = render_to_string('store/emails/order_status_update.txt', context)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[order.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send order status update email: {e}")
        return False

def send_welcome_email(user):
    """Send welcome email to new users"""
    subject = 'Welcome to Our E-commerce Store!'
    
    context = {
        'user': user,
    }
    
    html_message = render_to_string('store/emails/welcome.html', context)
    plain_message = render_to_string('store/emails/welcome.txt', context)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send welcome email: {e}")
        return False 