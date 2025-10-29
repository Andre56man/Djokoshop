"""
URL configuration for ecommerce project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from shop import views as shop_views

urlpatterns = [
    # Project-level routes that should override the admin catch-all
    path('admin/dashboard/', shop_views.admin_dashboard, name='admin_dashboard'),
    path('admin/user/edit/<int:user_id>/', shop_views.admin_edit_user, name='admin_edit_user'),
    path('admin/user/delete/<int:user_id>/', shop_views.admin_delete_user, name='admin_delete_user'),

    # Default Django admin (kept after custom admin views)
    path('admin/', admin.site.urls),

    # Application URLs
    path('', include('shop.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

