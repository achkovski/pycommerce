from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from store.models import Coupon, Product

from .cart import Cart
from .forms import CouponApplyForm


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, pk=product_id, is_available=True)
    try:
        quantity = max(1, int(request.POST.get('quantity', 1)))
    except (TypeError, ValueError):
        quantity = 1
    override = request.POST.get('override') == 'true'
    cart.add(product, quantity=quantity, override_quantity=override)
    if request.POST.get('next') == 'cart':
        return redirect('cart:detail')
    return redirect(product.get_absolute_url())


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, pk=product_id)
    cart.remove(product)
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
