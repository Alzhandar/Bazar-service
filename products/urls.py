from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, 
    ProductViewSet,
    ProductListView,
    ProductDetailView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    
)

app_name = 'products'

api_router = DefaultRouter()
api_router.register('categories', CategoryViewSet, basename='category-api')
api_router.register('products', ProductViewSet, basename='product-api')

web_urlpatterns = [
    path('', ProductListView.as_view(), name='product-list'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('create/', ProductCreateView.as_view(), name='product-create'),
    path('<int:pk>/edit/', ProductUpdateView.as_view(), name='product-edit'),
    path('<int:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'), 

]

urlpatterns = web_urlpatterns + [
    path('api/', include((api_router.urls, 'products-api'))),
]