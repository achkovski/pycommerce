import os

from django.contrib import messages
from django.db.models import Q
from django.http import FileResponse, Http404, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import ContactForm
from .models import Category, Hero, Product


def _available_products():
    return Product.objects.filter(is_available=True).select_related('category')


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
    products = _available_products()
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
    product = get_object_or_404(_available_products(), slug=slug)
    related = (
        _available_products()
        .filter(category=product.category)
        .exclude(pk=product.pk)[:4]
    )
    return render(request, 'store/product_detail.html', {
        'product': product,
        'related_products': related,
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
    products = _available_products().exclude(downloadable_file='')
    return render(request, 'store/downloads.html', {'products': products})


def download_file(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_available=True)
    if not product.downloadable_file:
        raise Http404('This product has no downloadable file.')
    response = FileResponse(product.downloadable_file.open('rb'), as_attachment=True)
    response['Content-Disposition'] = (
        f'attachment; filename="{os.path.basename(product.downloadable_file.name)}"'
    )
    return response
