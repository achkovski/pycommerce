from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from store.models import Order


@login_required
def profile(request):
    recent_orders = Order.objects.filter(user=request.user).prefetch_related('items__product')[:5]
    return render(request, 'account/profile.html', {'recent_orders': recent_orders})


@login_required
def orders(request):
    user_orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    return render(request, 'account/orders.html', {'orders': user_orders})
