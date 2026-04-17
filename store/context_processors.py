from .models import Category, SiteSettings


def categories(request):
    return {'nav_categories': Category.objects.all()}


def site_settings(request):
    return {'site_settings': SiteSettings.load()}
