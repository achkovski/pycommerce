from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from store.models import Coupon, Product

from .cart import Cart
from .forms import CouponApplyForm


VARIANT_PREFIX = 'variant_'


def _parse_variants(product: Product, post) -> dict:
    """Read `variant_<GroupName>` fields from POST and validate them.

    Only values that match a configured option on the product are kept, and
    every defined group must be chosen — otherwise an empty dict is returned so
    the caller can surface an error.
    """
    defined_groups: dict[str, set[str]] = {}
    for opt in product.variant_options.all():
        defined_groups.setdefault(opt.group_name, set()).add(opt.value)
    if not defined_groups:
        return {}
    selected: dict[str, str] = {}
    for key, value in post.items():
        if not key.startswith(VARIANT_PREFIX):
            continue
        group = key[len(VARIANT_PREFIX):]
        if group in defined_groups and value in defined_groups[group]:
            selected[group] = value
    if set(selected.keys()) != set(defined_groups.keys()):
        return {}
    return selected


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, pk=product_id, is_available=True)
    try:
        quantity = max(1, int(request.POST.get('quantity', 1)))
    except (TypeError, ValueError):
        quantity = 1
    override = request.POST.get('override') == 'true'

    has_variants = product.variant_options.exists()
    variants = _parse_variants(product, request.POST) if has_variants else {}
    if has_variants and not variants:
        messages.error(request, 'Please choose an option for each variant before adding to the cart.')
        return redirect(product.get_absolute_url())

    cart.add(product, quantity=quantity, override_quantity=override, variants=variants)
    if request.POST.get('next') == 'cart':
        return redirect('cart:detail')
    return redirect(product.get_absolute_url())


@require_POST
def cart_remove(request):
    key = request.POST.get('key', '')
    if key:
        Cart(request).remove(key)
    return redirect('cart:detail')


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/cart.html', {
        'cart': cart,
        'coupon_form': CouponApplyForm(),
    })


@require_POST
def coupon_apply(request):
    form = CouponApplyForm(request.POST)
    if form.is_valid():
        code = form.cleaned_data['code'].strip()
        try:
            coupon = Coupon.objects.get(code__iexact=code)
        except Coupon.DoesNotExist:
            messages.error(request, f'Coupon "{code}" not found.')
            return redirect('cart:detail')
        if not coupon.is_valid():
            messages.error(request, f'Coupon "{code}" is expired or no longer valid.')
            return redirect('cart:detail')
        request.session['coupon_id'] = coupon.pk
        messages.success(request, f'Coupon "{coupon.code}" applied ({coupon.discount_percent}% off).')
    else:
        messages.error(request, 'Please enter a coupon code.')
    return redirect('cart:detail')


@require_POST
def coupon_remove(request):
    request.session.pop('coupon_id', None)
    messages.info(request, 'Coupon removed.')
    return redirect('cart:detail')
