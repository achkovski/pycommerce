import os

from django.contrib import messages
from django.db.models import Q
from django.http import FileResponse, Http404, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import ContactForm
from .models import Category, Hero, OrderItem, Product, ProductSection


def _available_products():
    return Product.objects.filter(is_available=True).select_related('category')


def _physical_products():
    return _available_products().filter(category__is_digital=False)


def _purchased_product_ids(user):
    if not user.is_authenticated:
        return set()
    return set(
        OrderItem.objects
        .filter(order__user=user, order__is_paid=True)
        .values_list('product_id', flat=True)
    )


def home(request):
    hero = Hero.objects.filter(is_active=True).first()
    featured_products = (
        _available_products()
        .filter(is_featured=True)
        .order_by('featured_order', '-created_at')[:8]
    )
    featured_categories = (
        Category.objects
        .filter(is_featured_on_home=True)
        .order_by('featured_order', 'name')
    )
    on_sale = _available_products().filter(sale_price__isnull=False)[:4]
    return render(request, 'store/home.html', {
        'hero': hero,
        'featured_products': featured_products,
        'featured_categories': featured_categories,
        'on_sale_products': on_sale,
    })


def shop(request):
    query = request.GET.get('q', '').strip()
    products = _physical_products()
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    return render(request, 'store/shop.html', {
        'products': products,
        'query': query,
        'active_category': None,
    })


def product_detail(request, slug):
    product = get_object_or_404(
        _available_products().prefetch_related('images', 'variant_options'),
        slug=slug,
    )
    related = (
        _available_products()
        .filter(category=product.category)
        .exclude(pk=product.pk)[:4]
    )
    user_has_purchased = (
        product.is_digital
        and not product.is_free
        and product.pk in _purchased_product_ids(request.user)
    )
    sections = ProductSection.objects.filter(is_active=True).filter(
        Q(scope=ProductSection.SCOPE_GLOBAL)
        | Q(scope=ProductSection.SCOPE_CATEGORY, category=product.category)
        | Q(scope=ProductSection.SCOPE_PRODUCT, product=product)
    )
    return render(request, 'store/product_detail.html', {
        'product': product,
        'related_products': related,
        'user_has_purchased': user_has_purchased,
        'product_sections': sections,
        'variant_groups': product.variant_groups(),
    })


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = _available_products().filter(category=category)
    return render(request, 'store/shop.html', {
        'products': products,
        'query': '',
        'active_category': category,
    })


def about(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thanks! Your message has been received — we\'ll get back to you soon.')
            return redirect(reverse('store:about') + '#contact')
    else:
        form = ContactForm()
    return render(request, 'store/about.html', {'form': form})


def contact_redirect(request):
    return HttpResponsePermanentRedirect(reverse('store:about') + '#contact')


def downloads(request):
    products = (
        _available_products()
        .filter(category__is_digital=True)
        .exclude(downloadable_file='')
    )
    purchased_ids = _purchased_product_ids(request.user)
    return render(request, 'store/downloads.html', {
        'products': products,
        'purchased_ids': purchased_ids,
    })


def download_file(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_available=True)
    if not product.downloadable_file:
        raise Http404('This product has no downloadable file.')
    if not product.is_free:
        if not request.user.is_authenticated:
            messages.info(request, 'Sign in to access your downloads.')
            return redirect(reverse('account_login') + f'?next={request.path}')
        if product.pk not in _purchased_product_ids(request.user):
            messages.error(request, 'Purchase this item to download it.')
            return redirect(product.get_absolute_url())
    response = FileResponse(product.downloadable_file.open('rb'), as_attachment=True)
    response['Content-Disposition'] = (
        f'attachment; filename="{os.path.basename(product.downloadable_file.name)}"'
    )
    return response
