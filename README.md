# PyCommerce

A full-featured e-commerce web application built with Django 6. Covers product listings, variants, a session-based cart, coupons, user accounts, file downloads, and a configurable storefront via an admin-managed `SiteSettings` singleton.

---

## Tech stack

| Layer | Technology |
|---|---|
| Language | Python 3.14+ |
| Framework | Django 6.x |
| Database | PostgreSQL (Neon.tech) |
| Styling | Tailwind CSS (CDN) |
| Admin UI | django-unfold |
| Auth | django-allauth |
| Map | Leaflet.js + OpenStreetMap |

---

## Project structure

```
.
├── PyCommerce/           # Project config (settings, urls, wsgi)
├── store/                # Core app — products, categories, orders, site settings
│   ├── models.py         # Category, Product, Coupon, Order, Hero, SiteSettings …
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── forms.py
├── cart/                 # Session-based cart
│   ├── cart.py           # Cart class
│   ├── models.py         # (coupon session helpers)
│   └── views.py
├── accounts/             # User profile & order history
├── templates/
│   ├── base.html
│   ├── store/            # home, shop, product_detail, about, downloads …
│   ├── cart/
│   └── account/          # profile, orders, login, signup …
├── static/               # CSS, JS, images
├── media/                # Uploaded files (gitignored)
└── requirements.txt
```

---

## Pages

| URL | Page |
|---|---|
| `/` | Home — hero, featured products, category spotlights |
| `/shop/` | Shop — search, filters |
| `/shop/<slug>/` | Product detail — variants, add to cart |
| `/shop/category/<slug>/` | Category listing |
| `/about/` | About & Contact — story, video, map, contact form |
| `/cart/` | Cart — quantities, coupon code |
| `/downloads/` | Digital downloads |
| `/account/profile/` | User profile |
| `/account/orders/` | Order history |
| `/admin/` | Django admin (django-unfold) |

---

## Local setup

### 1. Clone and create a virtual environment

```bash
git clone <repo-url>
cd DjangoProject
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://user:password@host/dbname
```

A `DATABASE_URL` pointing at a PostgreSQL instance is required (local or [Neon.tech](https://neon.tech) free tier).

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Create a superuser

```bash
python manage.py createsuperuser
```

### 6. Collect static files (production only)

```bash
python manage.py collectstatic
```

### 7. Start the development server

```bash
python manage.py runserver
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

## Admin

Access the admin at `/admin/`. Key areas:

- **Site Settings** — store name, branding, about-page copy, video, map coordinates, homepage toggles
- **Hero sections** — manage the home-page hero banner
- **Products / Categories** — manage the catalogue, variants, images, downloadable files
- **Coupons** — create discount codes
- **Orders** — view and manage orders
- **Contact messages** — read messages submitted via the About page

---

## Deployment

The project is ready to deploy to [Render](https://render.com) or [Railway](https://railway.app).

**Build command:**
```bash
pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
```

**Start command:**
```bash
gunicorn PyCommerce.wsgi
```

**Required environment variables:** `SECRET_KEY`, `DEBUG=False`, `DATABASE_URL`, `ALLOWED_HOSTS`.
