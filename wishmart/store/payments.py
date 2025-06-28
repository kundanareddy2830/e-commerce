import stripe
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Order
import json

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_payment_intent(request, order_id):
    """Create a payment intent for Stripe"""
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        
        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=int(order.get_total_cost() * 100),  # Convert to cents
            currency='usd',
            metadata={'order_id': order.id}
        )
        
        return JsonResponse({
            'client_secret': intent.client_secret,
            'publishable_key': settings.STRIPE_PUBLISHABLE_KEY
        })
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhooks"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        order_id = payment_intent['metadata']['order_id']
        
        try:
            order = Order.objects.get(id=order_id)
            order.paid = True
            order.save()
        except Order.DoesNotExist:
            pass

    return JsonResponse({'status': 'success'})

def process_payment(request, order_id):
    """Process payment for an order"""
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        
        if request.method == 'POST':
            # Handle payment processing here
            # This would typically involve creating a payment intent
            # and redirecting to Stripe Checkout or handling card details
            
            # For now, we'll just mark as paid (demo mode)
            order.paid = True
            order.save()
            
            return JsonResponse({'status': 'success'})
            
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    
    return JsonResponse({'error': 'Invalid request'}, status=400) 