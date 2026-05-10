from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('register/', views.register_view, name='register'),  # ✅ new
    path('login/', views.login_view, name='login'),            # ✅ new
    path('logout/', views.logout_view, name='logout'),         # ✅ new
]