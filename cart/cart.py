from decimal import Decimal

from django.conf import settings

from store.models import Coupon, Product


class Cart:
    """Session-backed shopping cart.

    Items are keyed by a composite of product id and selected variant values so
    the same product with different variant choices occupies separate lines.
    """

    def __init__(self, request):
        self.session = request.session
        self.cart = self.session.setdefault(settings.CART_SESSION_ID, {})

    @staticmethod
    def _make_key(product_id, variants: dict | None) -> str:
        if not variants:
            return str(product_id)
        parts = [f'{k}={variants[k]}' for k in sorted(variants.keys())]
        return f'{product_id}|' + '|'.join(parts)

    @staticmethod
    def _compute_price(product: Product, variants: dict | None) -> Decimal:
        price = product.final_price
        if not variants:
            return price
        lookup = {
            (opt.group_name, opt.value): opt.price_delta
            for opt in product.variant_options.all()
            if opt.price_delta is not None
        }
        for group, value in variants.items():
            delta = lookup.get((group, value))
            if delta is not None:
                price = price + delta
        return price

    def add(self, product: Product, quantity: int = 1, override_quantity: bool = False,
            variants: dict | None = None) -> None:
        variants = variants or {}
        key = self._make_key(product.pk, variants)
        price = self._compute_price(product, variants)
        if key not in self.cart:
            self.cart[key] = {
                'product_id': product.pk,
                'quantity': 0,
                'price': str(price),
                'variants': variants,
            }
        if override_quantity:
            self.cart[key]['quantity'] = quantity
        else:
            self.cart[key]['quantity'] += quantity
        self.cart[key]['price'] = str(price)
        self.cart[key]['variants'] = variants
        self.cart[key]['product_id'] = product.pk
        self.save()

    def remove(self, key: str) -> None:
        if key in self.cart:
            del self.cart[key]
            self.save()

    def clear(self) -> None:
        self.session[settings.CART_SESSION_ID] = {}
        self.session.modified = True

    def save(self) -> None:
        self.session.modified = True

    def _resolve_product_id(self, key: str, item: dict) -> int | None:
        pid = item.get('product_id')
        if pid is not None:
            return pid
        # Legacy entries used the product id as the raw key.
        head = key.split('|', 1)[0]
        return int(head) if head.isdigit() else None

    def __iter__(self):
        product_ids = {
            self._resolve_product_id(key, item)
            for key, item in self.cart.items()
        }
        product_ids.discard(None)
        products = Product.objects.filter(pk__in=product_ids).select_related('category')
        product_map = {p.pk: p for p in products}
        for key, item in self.cart.items():
            pid = self._resolve_product_id(key, item)
            product = product_map.get(pid) if pid is not None else None
            if product is None:
                continue
            price = Decimal(item['price'])
            quantity = item['quantity']
            yield {
                'key': key,
                'product': product,
                'quantity': quantity,
                'price': price,
                'subtotal': price * quantity,
                'variants': item.get('variants') or {},
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
