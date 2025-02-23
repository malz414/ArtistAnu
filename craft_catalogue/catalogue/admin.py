from django.contrib import admin
from .models import Artist, CraftItem, Category, FeaturedItem, CraftItemImage, CartItem, CustomUser

class CategoryInline(admin.TabularInline):  # Inline form for categories
    model = CraftItem.categories.through  # This allows ManyToMany edits
    extra = 1  # Number of empty fields to show for adding new categories

class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'location', 'date_joined')
    search_fields = ('name', 'email')
    list_filter = ('location',)

# Customizing the CraftItem model in the admin
class CraftItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'artist', 'price', 'is_unique', 'quantity', 'is_sustainable', 'is_handmade')
    search_fields = ('name', 'categories__name')  # Search by category name
    list_filter = ('is_unique', 'is_sustainable', 'is_handmade')  # You can only filter by boolean fields directly
    filter_horizontal = ('categories',)  # Enables the ability to filter ManyToManyField more easily

    def get_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])
    get_categories.short_description = 'Categories'

    def get_cart_users(self, obj):
        return ", ".join(obj.get_cart_usernames()) if obj.get_cart_usernames() else "Not in Cart"
    get_cart_users.short_description = "In Carts"

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class CraftItemImageInline(admin.TabularInline):
    model = CraftItemImage
    extra = 1  

class CraftItemAdmin(admin.ModelAdmin):
    inlines = [CraftItemImageInline]

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_artist', 'is_staff', 'is_active')
    list_filter = ('is_artist', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_artist', 'is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_artist', 'is_staff', 'is_active'),
        }),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)

# Register the CustomUser model
admin.site.register(CustomUser, CustomUserAdmin)

admin.site.register(CraftItemImage)
admin.site.register(CraftItem, CraftItemAdmin)
# Registering models with customizations
admin.site.register(Artist, ArtistAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(FeaturedItem)
admin.site.register(CartItem)