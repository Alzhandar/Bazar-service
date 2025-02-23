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

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('items', ProductViewSet, basename='product')

api_urls = [
    path('', include(router.urls)),
]

web_urls = [
    path('', ProductListView.as_view(), name='product-list'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('create/', ProductCreateView.as_view(), name='product-create'),
    path('<int:pk>/edit/', ProductUpdateView.as_view(), name='product-edit'),
]

urlpatterns = web_urls + api_urls