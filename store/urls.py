from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='home'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/', views.product_list, name='products'),
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('register/', views.register_view, name='register'), 
    path('login/', views.login_view, name='login'),           
    path('logout/', views.logout_view, name='logout'),         
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
]
urlpatterns = [...] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)