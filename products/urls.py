from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, 
    ProductViewSet,
    ProductListView,
    ProductDetailView,
    ProductCreateView,
    ProductUpdateView
)

app_name = 'products'

# API роутер
api_router = DefaultRouter()
api_router.register('categories', CategoryViewSet, basename='category-api')
api_router.register('products', ProductViewSet, basename='product-api')

# URL паттерны для веб-интерфейса
web_urlpatterns = [
    path('', ProductListView.as_view(), name='product-list'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('create/', ProductCreateView.as_view(), name='product-create'),
    path('<int:pk>/edit/', ProductUpdateView.as_view(), name='product-edit'),
]

# Общие URL паттерны
urlpatterns = web_urlpatterns + [
    path('api/', include((api_router.urls, 'products-api'))),
]