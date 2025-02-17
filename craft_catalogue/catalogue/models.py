from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone



class FeaturedItem(models.Model):
    item = models.ForeignKey('CraftItem', on_delete=models.CASCADE, null=True, blank=True)
    artist = models.ForeignKey('Artist', on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=False)  # Allows easy toggling of featured content

    def __str__(self):
        return f"Featured: {self.item or self.artist}"

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    
    def __str__(self):
        return self.username

class Artist(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='artists/', blank=True, null=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    website = models.URLField(blank=True, null = True)
    social_media_links = models.JSONField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return self.name
    
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

from django.db import models

class CraftItem(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    artist = models.ForeignKey('Artist', on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category, related_name="items")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date_created = models.DateTimeField(auto_now_add=True)
    available = models.BooleanField(default=True)
    dimensions = models.CharField(max_length=255, blank=True)
    featured = models.BooleanField(default=False)
    is_unique = models.BooleanField(default=False)
    quantity = models.PositiveIntegerField(default=1)
    is_sustainable = models.BooleanField(default=False)
    is_handmade = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def in_cart(self):
        """Returns True if the item is currently in a cart."""
        return CartItem.objects.filter(item=self).exists()

    def get_cart_usernames(self):
        """Returns a list of users who have this item in their cart (for admin visibility)."""
        return list(Cart.objects.filter(cart_items__item=self).values_list('user__username', flat=True))

    
class CraftItemImage(models.Model):
    craft_item = models.ForeignKey(CraftItem, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='craft_items/')
    
    def __str__(self):
        return f"Image for {self.craft_item.name}"

class CartItem(models.Model):
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE, related_name='cart_items')
    item = models.ForeignKey(CraftItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)  

    @property
    def total_price(self):
        return self.quantity * self.item.price
    
    def is_expired(self):
        return timezone.now() - self.created_at > timezone.timedelta(minutes=30)

    def __str__(self):
        return f"{self.item.name} in {self.cart.user.username}'s cart"

class Cart(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    # Use string reference for CustomUser to avoid circular imports
    user = models.ForeignKey('catalogue.CustomUser', null=True, blank=True, on_delete=models.SET_NULL)
    
    def total_price(self):
        return sum(cart_item.total_price for cart_item in self.cart_items.all())

    def __str__(self):
        return f"Cart {self.id} for {self.user.username if self.user else 'Guest'}"

