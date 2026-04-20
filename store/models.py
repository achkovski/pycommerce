from decimal import Decimal

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.CharField(max_length=300, blank=True, help_text='Short tagline shown under the category title')
    image = models.ImageField(upload_to='categories/', blank=True)
    is_featured_on_home = models.BooleanField(default=False, help_text='Show this category as its own section on the home page')
    featured_order = models.PositiveIntegerField(default=0, help_text='Lower numbers appear first')
    featured_product_count = models.PositiveIntegerField(default=4, help_text='How many products to show in the home section')
    is_digital = models.BooleanField(default=False, help_text='Products in this category are digital downloads — excluded from the shop listings and shown on the Downloads page instead')
    shop_order = models.PositiveIntegerField(default=0, help_text='Controls the order categories (and their products) appear in the shop. Lower numbers appear first.')

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:category_detail', args=[self.slug])

    def featured_products(self):
        return self.products.filter(is_available=True).order_by('-created_at')[:self.featured_product_count]


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='products/')
    downloadable_file = models.FileField(upload_to='downloads/', blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, help_text='Show in the Featured section on the home page')
    featured_order = models.PositiveIntegerField(default=0, help_text='Lower numbers appear first in Featured')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['slug']), models.Index(fields=['-created_at'])]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.slug])

    @property
    def final_price(self) -> Decimal:
        return self.sale_price if self.sale_price is not None else self.price

    @property
    def is_on_sale(self) -> bool:
        return self.sale_price is not None and self.sale_price < self.price

    @property
    def is_free(self) -> bool:
        return self.final_price == 0

    @property
    def is_digital(self) -> bool:
        return self.category.is_digital

    def variant_groups(self):
        """Options grouped by their group_name, preserving first-seen order.

        Returns a list like ``[{'name': 'Size', 'options': [<opt>, ...]}, ...]``.
        Empty when the product has no configured variants.
        """
        groups: dict[str, list] = {}
        for opt in self.variant_options.all():
            groups.setdefault(opt.group_name, []).append(opt)
        return [{'name': name, 'options': opts} for name, opts in groups.items()]


class ProductVariantOption(models.Model):
    """One selectable value inside a variant group (e.g. Size → Medium).

    Options sharing the same ``group_name`` on a product form a single selector
    on the product page. ``price_delta`` is added to the product's base price
    when that option is chosen; leave it empty for no change.
    """

    product = models.ForeignKey(Product, related_name='variant_options', on_delete=models.CASCADE)
    group_name = models.CharField(
        max_length=100,
        help_text='Groups options into one selector. e.g. "Size", "Grind".',
    )
    value = models.CharField(max_length=100, help_text='e.g. "Small", "Whole bean".')
    price_delta = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Added to the base price when selected. Leave empty for no change.',
    )
    sort_order = models.PositiveIntegerField(default=0, help_text='Lower numbers appear first within the group.')

    class Meta:
        ordering = ['group_name', 'sort_order', 'id']
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'group_name', 'value'],
                name='uniq_product_variant_option',
            ),
        ]

    def __str__(self):
        return f'{self.group_name}: {self.value}'


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    alt = models.CharField(max_length=200, blank=True, help_text='Alt text for screen readers')
    sort_order = models.PositiveIntegerField(default=0, help_text='Lower numbers appear first')

    class Meta:
        ordering = ['sort_order', 'id']

    def __str__(self):
        return f'Image for {self.product.name}'


class ProductSection(models.Model):
    SCOPE_GLOBAL = 'global'
    SCOPE_CATEGORY = 'category'
    SCOPE_PRODUCT = 'product'
    SCOPE_CHOICES = [
        (SCOPE_GLOBAL, 'Global — show on every product'),
        (SCOPE_CATEGORY, 'Category — show on all products in a category'),
        (SCOPE_PRODUCT, 'Product — show on a single product'),
    ]

    title = models.CharField(max_length=200)
    body = models.TextField(help_text='Supports line breaks. Rendered as plain text.')
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, default=SCOPE_GLOBAL)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='product_sections',
        help_text='Required when scope is Category.',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sections',
        help_text='Required when scope is Product.',
    )
    is_collapsible = models.BooleanField(default=True, help_text='If off, the section always shows expanded with no toggle.')
    default_open = models.BooleanField(default=False, help_text='When collapsible, controls whether the section starts expanded.')
    sort_order = models.PositiveIntegerField(default=0, help_text='Lower numbers appear first')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['sort_order', 'id']

    def __str__(self):
        return f'{self.title} ({self.get_scope_display()})'

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.scope == self.SCOPE_CATEGORY and self.category_id is None:
            raise ValidationError({'category': 'Choose a category for a category-scoped section.'})
        if self.scope == self.SCOPE_PRODUCT and self.product_id is None:
            raise ValidationError({'product': 'Choose a product for a product-scoped section.'})
        if self.scope == self.SCOPE_GLOBAL and (self.category_id or self.product_id):
            raise ValidationError('Global sections must not have a category or product set.')


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.PositiveIntegerField(help_text='Integer percent, e.g. 20 = 20% off')
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)
    max_uses = models.PositiveIntegerField(default=100)
    times_used = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-valid_to']

    def __str__(self):
        return self.code

    def is_valid(self) -> bool:
        now = timezone.now()
        return (
            self.active
            and self.valid_from <= now <= self.valid_to
            and self.times_used < self.max_uses
        )


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='orders', on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.pk} ({self.user})'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'

    @property
    def subtotal(self) -> Decimal:
        return self.price * self.quantity


class Hero(models.Model):
    """Home-page hero section. Exactly one row should be marked active."""

    name = models.CharField(max_length=120, help_text='Internal label for this hero variant')
    badge_text = models.CharField(max_length=80, blank=True, help_text='Small pill shown above the headline')
    title = models.CharField(max_length=200)
    subtitle = models.TextField(blank=True)
    cta_primary_label = models.CharField(max_length=40, default='Browse the shop')
    cta_primary_url = models.CharField(max_length=200, default='/shop/')
    cta_secondary_label = models.CharField(max_length=40, blank=True)
    cta_secondary_url = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='hero/', blank=True, help_text='Optional right-side image')
    is_active = models.BooleanField(default=False, help_text='Only one hero should be active at a time')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_active', '-updated_at']
        verbose_name = 'hero section'
        verbose_name_plural = 'hero sections'

    def __str__(self):
        return f'{self.name}{" (active)" if self.is_active else ""}'

    def save(self, *args, **kwargs):
        if self.is_active:
            Hero.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class SiteSettings(models.Model):
    """Site-wide branding, about-page copy, contact info, and map coords.

    Singleton: the admin enforces exactly one row. Access via ``SiteSettings.load()``.
    """

    # Branding
    store_name = models.CharField(max_length=100, default='PyCommerce')
    store_tagline = models.CharField(max_length=200, blank=True, default='A modern Django storefront with a clean, simple checkout.')
    logo = models.ImageField(upload_to='branding/', blank=True, null=True, help_text='Optional — replaces the "P" badge in the navbar')
    favicon = models.ImageField(upload_to='branding/', blank=True, null=True)

    # Contact info (rendered on the About/Contact page)
    contact_email = models.EmailField(blank=True, default='hello@pycommerce.example')
    contact_phone = models.CharField(max_length=40, blank=True)
    contact_address_line = models.CharField(max_length=200, blank=True, default='PyCommerce HQ')
    contact_address = models.CharField(max_length=300, blank=True, default='ul. Marshal Tito 123, 7000 Bitola, North Macedonia')
    contact_hours = models.CharField(max_length=120, blank=True, default='Mon–Fri, 9:00–17:00')

    # Map (Leaflet/OpenStreetMap)
    map_latitude = models.DecimalField(max_digits=9, decimal_places=6, default=Decimal('41.029700'))
    map_longitude = models.DecimalField(max_digits=9, decimal_places=6, default=Decimal('21.329700'))
    map_zoom = models.PositiveSmallIntegerField(default=15)
    map_popup_title = models.CharField(max_length=120, default='PyCommerce HQ')
    map_popup_subtitle = models.CharField(max_length=200, blank=True, default='ul. Marshal Tito 123, Bitola')

    # About page — editable copy
    about_video_file = models.FileField(
        upload_to='about/',
        blank=True,
        null=True,
        help_text='Upload a video file (MP4 recommended). Takes priority over the URL below.',
    )
    about_video_url = models.URLField(
        blank=True,
        help_text='YouTube/Vimeo embed URL (e.g. https://www.youtube.com/embed/…). Used when no file is uploaded.',
    )
    about_badge = models.CharField(max_length=60, default='Our story')
    about_headline = models.CharField(max_length=200, default='Commerce, done properly.')
    about_lead = models.TextField(blank=True, default='PyCommerce is a modern online shop built with Django, combining a clean admin for store owners with a fast, simple checkout for customers.')
    about_body = models.TextField(blank=True, default='Our mission is straightforward: curate great products, price them fairly, and make browsing effortless.')
    about_stat_1_value = models.CharField(max_length=20, blank=True, default='10k+')
    about_stat_1_label = models.CharField(max_length=60, blank=True, default='Happy customers')
    about_stat_2_value = models.CharField(max_length=20, blank=True, default='500+')
    about_stat_2_label = models.CharField(max_length=60, blank=True, default='Products curated')
    about_stat_3_value = models.CharField(max_length=20, blank=True, default='4.9')
    about_stat_3_label = models.CharField(max_length=60, blank=True, default='Avg. review score')
    about_stat_4_value = models.CharField(max_length=20, blank=True, default='24h')
    about_stat_4_label = models.CharField(max_length=60, blank=True, default='Typical ship time')

    # Homepage section visibility toggles
    show_featured_products = models.BooleanField(default=True)
    show_on_sale_section = models.BooleanField(default=True)
    show_category_sections = models.BooleanField(default=True)
    show_newsletter_section = models.BooleanField(default=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'site settings'
        verbose_name_plural = 'site settings'

    def __str__(self):
        return self.store_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Singleton — prevent deletion
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} <{self.email}> — {self.subject or "(no subject)"}'
