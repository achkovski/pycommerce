from .models import Category, SiteSettings


def categories(request):
    return {'nav_categories': Category.objects.filter(is_digital=False)}


def site_settings(request):
    return {'site_settings': SiteSettings.load()}
