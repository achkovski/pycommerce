from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import Category, ContactMessage, Coupon, Hero, Order, OrderItem, Product, SiteSettings


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ['name', 'slug', 'is_featured_on_home', 'featured_order', 'featured_product_count']
    list_editable = ['is_featured_on_home', 'featured_order', 'featured_product_count']
    list_filter = ['is_featured_on_home']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'description', 'image')}),
        ('Homepage', {
            'fields': ('is_featured_on_home', 'featured_order', 'featured_product_count'),
            'description': 'Control how this category appears as a spotlight section on the home page.',
        }),
    )


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ['name', 'category', 'price', 'sale_price', 'stock', 'is_available', 'is_featured', 'created_at']
    list_filter = ['category', 'is_available', 'is_featured', 'created_at']
    list_editable = ['price', 'sale_price', 'stock', 'is_available', 'is_featured']
    list_filter_submit = True
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        (None, {'fields': ('category', 'name', 'slug', 'description', 'image')}),
        ('Pricing & stock', {'fields': ('price', 'sale_price', 'stock', 'is_available')}),
        ('Homepage', {'fields': ('is_featured', 'featured_order')}),
        ('Download', {'fields': ('downloadable_file',)}),
        ('Metadata', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(Coupon)
class CouponAdmin(ModelAdmin):
    list_display = ['code', 'discount_percent', 'valid_from', 'valid_to', 'active', 'times_used', 'max_uses']
    list_filter = ['active']
    search_fields = ['code']


class OrderItemInline(TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ['id', 'user', 'total_price', 'coupon', 'is_paid', 'created_at']
    list_filter = ['is_paid', 'created_at']
    list_filter_submit = True
    search_fields = ['user__username', 'user__email']
    inlines = [OrderItemInline]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ContactMessage)
class ContactMessageAdmin(ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    list_editable = ['is_read']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at']


@admin.register(SiteSettings)
class SiteSettingsAdmin(ModelAdmin):
    fieldsets = (
        ('Branding', {
            'fields': ('store_name', 'store_tagline', 'logo', 'favicon'),
            'description': 'Shown in the navbar, footer and browser tab across the site.',
        }),
        ('Contact information', {
            'fields': ('contact_email', 'contact_phone', 'contact_address_line', 'contact_address', 'contact_hours'),
            'description': 'Rendered on the About & Contact page and in the footer.',
        }),
        ('Map location', {
            'fields': ('map_latitude', 'map_longitude', 'map_zoom', 'map_popup_title', 'map_popup_subtitle'),
            'description': 'Leaflet + OpenStreetMap. Tip: right-click on openstreetmap.org to copy lat/lng.',
        }),
        ('About page — copy', {
            'fields': ('about_badge', 'about_headline', 'about_lead', 'about_body'),
        }),
        ('About page — stats', {
            'fields': (
                ('about_stat_1_value', 'about_stat_1_label'),
                ('about_stat_2_value', 'about_stat_2_label'),
                ('about_stat_3_value', 'about_stat_3_label'),
                ('about_stat_4_value', 'about_stat_4_label'),
            ),
            'description': 'Four headline metrics in the About page grid. Leave value blank to hide a stat.',
        }),
        ('Home page sections', {
            'fields': ('show_featured_products', 'show_on_sale_section', 'show_category_sections', 'show_newsletter_section'),
            'description': 'Toggle which sections appear on the home page.',
        }),
    )
    readonly_fields = ['updated_at']

    def has_add_permission(self, request):
        # Singleton — allow only if no row exists yet
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        # Skip changelist — send straight to the single row's change page
        obj = SiteSettings.load()
        from django.shortcuts import redirect
        from django.urls import reverse
        return redirect(reverse('admin:store_sitesettings_change', args=[obj.pk]))


@admin.register(Hero)
class HeroAdmin(ModelAdmin):
    list_display = ['name', 'title', 'is_active', 'updated_at']
    list_filter = ['is_active']
    fieldsets = (
        (None, {'fields': ('name', 'is_active')}),
        ('Content', {'fields': ('badge_text', 'title', 'subtitle', 'image')}),
        ('Primary call to action', {'fields': ('cta_primary_label', 'cta_primary_url')}),
        ('Secondary call to action (optional)', {'fields': ('cta_secondary_label', 'cta_secondary_url')}),
    )
