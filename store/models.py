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
