from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    UserViewSet, 
    CustomLoginView, 
    CustomLogoutView,
    UserProfileView, 
    UserUpdateView, 
    UserListView
)

app_name = 'users'

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')

api_urls = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

web_urls = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/edit/', UserUpdateView.as_view(), name='profile-edit'),
    path('users/', UserListView.as_view(), name='user-list'),
]
urlpatterns = web_urls + api_urls + router.urls