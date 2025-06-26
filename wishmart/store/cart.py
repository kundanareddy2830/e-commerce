from decimal import Decimal
from django.conf import settings
from .models import Product

class Cart(object):
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        products_map = {str(product.id): product for product in products}
        for product_id, item in self.cart.items():
            product = products_map.get(product_id)
            item_copy = item.copy()
            item_copy['product'] = product
            item_copy['price'] = float(Decimal(item_copy['price']))
            item_copy['total_price'] = float(item_copy['price'] * item_copy['quantity'])
            yield item_copy

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return float(sum(float(Decimal(item['price'])) * item['quantity'] for item in self.cart.values()))

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True 