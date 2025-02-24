from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Trading Platform API",
        default_version='v1',
        description="API documentation for Trading Platform",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@trading-platform.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)



urlpatterns = [
    path('', RedirectView.as_view(pattern_name='products:product-list', permanent=False), name='home'),
    path('admin/', admin.site.urls),
    
    path('api/docs/swagger/', schema_view.with_ui('swagger', cache_timeout=0), 
         name='schema-swagger-ui'),
    path('api/docs/redoc/', schema_view.with_ui('redoc', cache_timeout=0), 
         name='schema-redoc'),
    
    path('api/', include([
        path('users/', include(('users.urls', 'users'), namespace='users-api')),
        path('products/', include(('products.urls', 'products'), namespace='products-api')),
        path('trading/', include(('trading.urls', 'trading'), namespace='trading-api')),
        path('sales/', include(('sales.urls', 'sales'), namespace='sales-api')),
        path('analytics/', include(('analytics.urls', 'analytics'), namespace='analytics-api')),
    ])),
    
    path('', include('users.urls')),
    path('products/', include('products.urls', namespace='products')),  
    path('trading/', include('trading.urls')),
    path('sales/', include('sales.urls')),
    path('analytics/', include('analytics.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)