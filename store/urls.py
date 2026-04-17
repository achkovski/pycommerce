from django.urls import path

from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('shop/category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('shop/<slug:slug>/', views.product_detail, name='product_detail'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact_redirect, name='contact'),
    path('downloads/', views.downloads, name='downloads'),
    path('downloads/<int:product_id>/', views.download_file, name='download_file'),
]
