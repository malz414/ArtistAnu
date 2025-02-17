"""
URL configuration for craft_catalogue project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import logout_view, all_categories, search_suggestions, search_items
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search_items/', search_items, name='search_items'),
    path('search-suggestions/', search_suggestions, name='search_suggestions'),

    path('cart/remove-expired/', views.remove_expired_items, name='remove_expired_items'),
    path('category/<str:category_name>/', views.category_items, name='category_items'),
    path('catalogue/', views.catalogue, name='catalogue'),    
    path('add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),   # Use item_name instead of item_id
    path('item/<str:item_name>/', views.item_detail, name='item_detail'),  # This is the item detail page URL
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('categories/', all_categories, name='all_categories'),
    path('login/', views.custom_login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),

    path('dashboard/', views.dashboard, name='dashboard'),
    
    path('artist_list/', views.artist_list, name='artist_list'),
    path('craft-items/', views.craft_item_list, name='craft_item_list'),

    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),

    path('artists/', views.artist_list, name='artist_list'),
    path('artist/<str:artist_name>/', views.artist_detail, name='artist_detail'), 
    path('checkout/complete/', views.complete_checkout, name='complete_checkout'),  # Define this URL pattern

    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

] 
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)