# Django E-Commerce Project — Requirements & Stack Reference

## Project Overview

A full-featured e-commerce web application built with Django, covering all university assignment requirements. The project will demonstrate MVC/MVT architecture, database design, authentication, and modern web development practices.

---

## Assignment Requirements Checklist

| # | Requirement | Status |
|---|-------------|--------|
| 1 | Minimum 5 pages (Home, About, Shop, Contact, Product Detail) | ⬜ |
| 2 | One external page (link to an external resource/partner) | ⬜ |
| 3 | Product search functionality | ⬜ |
| 4 | Easy and seamless navigation | ⬜ |
| 5 | Good design and UI/UX | ⬜ |
| 6 | Product cards and product detail/info pages | ⬜ |
| 7 | Product categories | ⬜ |
| 8 | Promotions and coupons | ⬜ |
| 9 | Cart and user account | ⬜ |
| 10 | File download | ⬜ |
| 11 | Map (company location via OpenStreetMap/Leaflet.js) | ⬜ |

---

## Pages

| Page | URL | Description |
|------|-----|-------------|
| Home | `/` | Hero banner, featured products, promotions |
| Shop | `/shop/` | All products with filters and search |
| Product Detail | `/shop/<slug>/` | Full product info, add to cart |
| Category | `/shop/category/<slug>/` | Products filtered by category |
| About | `/about/` | Company info + embedded map |
| Contact | `/contact/` | Contact form + map |
| Cart | `/cart/` | Shopping cart with coupon input |
| Account | `/account/` | User profile, order history |
| Login / Register | `/accounts/login/`, `/accounts/register/` | Auth pages via django-allauth |
| Downloads | `/downloads/` | File download page |
| External Link | N/A | Link to an external partner/resource in navbar or footer |

---

## Tech Stack

### Core

| Layer         | Technology                                | Notes |
|---------------|-------------------------------------------|-------|
| Language      | Python 3.12+                              | |
| Framework     | Django 5.x                                | Full-stack, batteries included |
| Database      | Neon.tech PostgreSQL                      | Easy swap via `DATABASE_URL` env var |
| Styling       | Tailwind CSS (via CDN or django-tailwind) | Utility-first, fast to style |
| Template engine | Django Templates (Jinja2-compatible)      | Server-side rendering |
| Map           | Leaflet.js + OpenStreetMap                | No API key needed |

### Key Python Packages

```
django>=5.0
django-allauth          # Authentication (register, login, social auth)
Pillow                  # Image uploads for product photos
django-crispy-forms     # Beautiful form rendering
crispy-tailwind         # Tailwind adapter for crispy-forms
whitenoise              # Serve static files in production
python-decouple         # Environment variable management (.env)
gunicorn                # WSGI server for deployment
psycopg2-binary         # PostgreSQL driver (for prod)
```

Install all at once:
```bash
pip install django django-allauth Pillow django-crispy-forms crispy-tailwind whitenoise python-decouple gunicorn psycopg2-binary
```

---

## Project Structure

```
ecommerce/
├── manage.py
├── requirements.txt
├── .env
├── ecommerce/                  # Project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── store/                      # Main app
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── forms.py
├── cart/                       # Cart app
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── cart.py                 # Session-based cart logic
├── accounts/                   # User account app
│   ├── views.py
│   └── urls.py
├── templates/
│   ├── base.html               # Base layout with navbar + footer
│   ├── store/
│   │   ├── home.html
│   │   ├── shop.html
│   │   ├── product_detail.html
│   │   ├── category.html
│   │   ├── about.html
│   │   └── contact.html
│   ├── cart/
│   │   └── cart.html
│   └── account/
│       ├── profile.html
│       └── orders.html
├── static/
│   ├── css/
│   ├── js/
│   └── images/
└── media/                      # User-uploaded files (product images)
```

---

## Data Models

### Product

```python
class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='categories/', blank=True)

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='products/')
    downloadable_file = models.FileField(upload_to='downloads/', blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### Coupon

```python
class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.PositiveIntegerField()  # e.g. 20 for 20%
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)
    max_uses = models.PositiveIntegerField(default=100)
    times_used = models.PositiveIntegerField(default=0)
```

### Order

```python
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
```

---

## Feature Implementation Guide

### 1. Search

```python
# views.py
def shop(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(is_available=True)
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    return render(request, 'store/shop.html', {'products': products, 'query': query})
```

### 2. Session-Based Cart

```python
# cart/cart.py
class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product, quantity=1):
        pid = str(product.id)
        if pid not in self.cart:
            self.cart[pid] = {'quantity': 0, 'price': str(product.price)}
        self.cart[pid]['quantity'] += quantity
        self.save()

    def save(self):
        self.session.modified = True
```

### 3. Coupon Application

```python
# views.py
def apply_coupon(request):
    code = request.POST.get('code')
    try:
        coupon = Coupon.objects.get(
            code=code,
            active=True,
            valid_from__lte=timezone.now(),
            valid_to__gte=timezone.now()
        )
        request.session['coupon_id'] = coupon.id
    except Coupon.DoesNotExist:
        messages.error(request, 'Invalid or expired coupon.')
    return redirect('cart')
```

### 4. File Download

```python
# views.py
from django.http import FileResponse
import os

def download_file(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if not product.downloadable_file:
        raise Http404
    response = FileResponse(open(product.downloadable_file.path, 'rb'))
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(product.downloadable_file.name)}"'
    return response
```

### 5. Map (Leaflet.js + OpenStreetMap)

Add to `about.html` or `contact.html`:

```html
<!-- In <head> -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<!-- In <body> -->
<div id="map" style="height: 400px;"></div>

<script>
  const map = L.map('map').setView([41.0297, 21.3297], 15); // Bitola coords as example
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(map);
  L.marker([41.0297, 21.3297])
    .addTo(map)
    .bindPopup('<b>Our Store</b><br>123 Main Street')
    .openPopup();
</script>
```

### 6. External Page Link

Add to the navbar in `base.html`:

```html
<a href="https://some-external-partner.com" target="_blank" rel="noopener noreferrer">
  Our Partner ↗
</a>
```

Or implement as a Django redirect view:

```python
# urls.py
from django.views.generic import RedirectView
path('partner/', RedirectView.as_view(url='https://external-site.com'), name='partner'),
```

---

## Django Admin Setup

Register your models for free back-office management:

```python
# store/admin.py
from django.contrib import admin
from .models import Product, Category, Coupon, Order

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'is_available']
    list_filter = ['category', 'is_available']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Category)
admin.site.register(Coupon)
admin.site.register(Order)
```

Access at `/admin/` after running `python manage.py createsuperuser`.

---

## Setup & Run

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
echo "SECRET_KEY=your-secret-key-here" > .env
echo "DEBUG=True" >> .env

# 4. Run migrations
python manage.py makemigrations
python manage.py migrate

# 5. Create superuser (for admin panel)
python manage.py createsuperuser

# 6. Collect static files
python manage.py collectstatic

# 7. Start development server
python manage.py runserver
```

---

## Deployment (Render or Railway — Free Tier)

1. Push project to GitHub
2. Create a new Web Service on [render.com](https://render.com) or [railway.app](https://railway.app)
3. Set environment variables: `SECRET_KEY`, `DEBUG=False`, `DATABASE_URL`
4. Set build command: `pip install -r requirements.txt && python manage.py migrate`
5. Set start command: `gunicorn ecommerce.wsgi`

---

## Suggested Build Order

1. **Setup** — Create Django project, install packages, configure settings
2. **Models** — Define Category, Product, Coupon, Order, OrderItem
3. **Admin** — Register models, add seed data via admin panel
4. **Base template** — Navbar, footer, Tailwind setup
5. **Home & Shop pages** — ListView for products, category filter
6. **Product Detail page** — DetailView, add-to-cart button
7. **Cart** — Session cart, add/remove/update quantities
8. **Coupons** — Coupon model, apply coupon form in cart
9. **Authentication** — django-allauth setup, login/register/profile
10. **File download** — FileResponse view, link from product detail
11. **Map** — Leaflet.js on About/Contact page
12. **Search** — Q objects filter on shop view
13. **External link** — Add to navbar or footer
14. **Polish** — Responsive design, error pages (404/500), loading states

---

## Learning Resources

| Resource | URL |
|----------|-----|
| Django Official Tutorial | https://docs.djangoproject.com/en/5.0/intro/tutorial01/ |
| Django ORM Queries | https://docs.djangoproject.com/en/5.0/topics/db/queries/ |
| django-allauth docs | https://docs.allauth.org/en/latest/ |
| Tailwind CSS docs | https://tailwindcss.com/docs |
| Leaflet.js docs | https://leafletjs.com/reference.html |
| OpenStreetMap tiles | https://wiki.openstreetmap.org/wiki/Tile_servers |
| Render deployment guide | https://render.com/docs/deploy-django |

---

user | achkovski.kiril@uklo.edu.mk | 1234