from decimal import Decimal

from django.conf import settings

from store.models import Coupon, Product


class Cart:
    """Session-backed shopping cart. Items are keyed by product id (str)."""

    def __init__(self, request):
        self.session = request.session
        self.cart = self.session.setdefault(settings.CART_SESSION_ID, {})

    def add(self, product: Product, quantity: int = 1, override_quantity: bool = False) -> None:
        pid = str(product.pk)
        if pid not in self.cart:
            self.cart[pid] = {'quantity': 0, 'price': str(product.final_price)}
        if override_quantity:
            self.cart[pid]['quantity'] = quantity
        else:
            self.cart[pid]['quantity'] += quantity
        self.cart[pid]['price'] = str(product.final_price)
        self.save()

    def remove(self, product: Product) -> None:
        pid = str(product.pk)
        if pid in self.cart:
            del self.cart[pid]
            self.save()

    def clear(self) -> None:
        self.session[settings.CART_SESSION_ID] = {}
        self.session.modified = True

    def save(self) -> None:
        self.session.modified = True

    def __iter__(self):
        products = Product.objects.filter(pk__in=self.cart.keys()).select_related('category')
        product_map = {str(p.pk): p for p in products}
        for pid, item in self.cart.items():
            product = product_map.get(pid)
            if product is None:
                continue
            price = Decimal(item['price'])
            quantity = item['quantity']
            yield {
                'product': product,
                'quantity': quantity,
                'price': price,
                'subtotal': price * quantity,
            }

    def __len__(self) -> int:
        return sum(item['quantity'] for item in self.cart.values())

    @property
    def subtotal(self) -> Decimal:
        return sum(
            (Decimal(item['price']) * item['quantity'] for item in self.cart.values()),
            Decimal('0'),
        )

    @property
    def coupon(self):
        coupon_id = self.session.get('coupon_id')
        if not coupon_id:
            return None
        try:
            coupon = Coupon.objects.get(pk=coupon_id)
        except Coupon.DoesNotExist:
            return None
        return coupon if coupon.is_valid() else None

    @property
    def discount(self) -> Decimal:
        coupon = self.coupon
        if coupon is None:
            return Decimal('0')
        return (self.subtotal * Decimal(coupon.discount_percent) / Decimal('100')).quantize(Decimal('0.01'))

    @property
    def total(self) -> Decimal:
        return (self.subtotal - self.discount).quantize(Decimal('0.01'))
