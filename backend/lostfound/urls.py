from django.urls import path
from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()
router.register('items', views.ItemViewSet, basename='item')

urlpatterns = [
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('claims/', views.ClaimListCreateView.as_view(), name='claims'),
    path('claims/<int:pk>/decide/', views.ClaimDecideView.as_view(), name='claim-decide'),
    *router.urls,
]
