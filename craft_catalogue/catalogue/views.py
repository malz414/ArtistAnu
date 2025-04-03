# catalogue/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import CraftItem, Cart, CartItem, Artist, FeaturedItem, Category, CraftItemImage
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm  
# catalogue/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .forms import SignUpForm, CustomAuthenticationForm, ArtistProfileForm, ArtistSignUpForm  # Ensure these forms are defined in forms.py
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models.functions import Lower
from django.db.models import Q, Prefetch
from django.http import JsonResponse
from django.utils import timezone
from django.http import JsonResponse
from .forms import CraftItemForm, CraftItemImageForm, ArtistProfileForm
from django.forms import formset_factory
from decimal import Decimal
import json

@login_required
def add_craft_item(request):
    if not request.user.is_artist:
        return redirect('home')

    artist = get_object_or_404(Artist, user=request.user)
    ImageFormSet = formset_factory(CraftItemImageForm, extra=3)  # Allow up to 3 images

    if request.method == 'POST':
        item_form = CraftItemForm(request.POST)
        image_formset = ImageFormSet(request.POST, request.FILES)
        if item_form.is_valid() and image_formset.is_valid():
            # Save the CraftItem
            craft_item = item_form.save(commit=False)
            craft_item.artist = artist
            craft_item.save()
            item_form.save_m2m()

            # Save the CraftItemImages
            for form in image_formset:
                if form.cleaned_data.get('image'):
                    craft_item_image = form.save(commit=False)
                    craft_item_image.craft_item = craft_item
                    craft_item_image.save()

            return redirect('artist_dashboard')
    else:
        item_form = CraftItemForm()
        image_formset = ImageFormSet()

    return render(request, 'catalogue/add_craft_item.html', {
        'item_form': item_form,
        'image_formset': image_formset,
    })



@login_required
def edit_craft_item(request, item_id):
    if not request.user.is_artist:
        return redirect('home')

    artist = get_object_or_404(Artist, user=request.user)
    craft_item = get_object_or_404(CraftItem, id=item_id, artist=artist)
    existing_images = craft_item.images.all()  # Get existing images

    if request.method == 'POST':
        item_form = CraftItemForm(request.POST, instance=craft_item)
        image_form = CraftItemImageForm(request.POST, request.FILES)
        if item_form.is_valid() and image_form.is_valid():
            item_form.save()

            # Save the new image if provided
            if image_form.cleaned_data.get('image'):
                craft_item_image = image_form.save(commit=False)
                craft_item_image.craft_item = craft_item
                craft_item_image.save()

            # Handle image deletion
            if 'delete_images' in request.POST:
                deleted_image_ids = request.POST.getlist('delete_images')
                CraftItemImage.objects.filter(id__in=deleted_image_ids).delete()

            return redirect('artist_dashboard')
    else:
        item_form = CraftItemForm(instance=craft_item)  # Pre-fill the form with existing data
        image_form = CraftItemImageForm()

    return render(request, 'catalogue/edit_craft_item.html', {
        'item_form': item_form,
        'image_form': image_form,
        'existing_images': existing_images,  # Pass existing images to the template
    })



def search_items(request):
    query = request.GET.get('query', '')
    if query:
        # Fetch CraftItems and prefetch related images in a single query
        items = CraftItem.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).prefetch_related('images')[:5]  # Limiting to 5 items

        suggestions = []
        for item in items:
            # Get the first image associated with the CraftItem
            first_image = item.images.first()
            image_url = first_image.image.url if first_image else ''

            suggestions.append({
                'name': item.name,
                'image': image_url,  # Include image URL
                'price': str(item.price)  # Include price as a string
            })
        return JsonResponse({'items': suggestions})
    return JsonResponse({'items': []})

@login_required
def artist_dashboard(request):
    if not request.user.is_artist:
        return redirect('home')  # Redirect non-artists to the home page

    artist = get_object_or_404(Artist, user=request.user)
    craft_items = CraftItem.objects.filter(artist=artist)

    return render(request, 'catalogue/artist_dashboard.html', {
        'artist': artist,
        'craft_items': craft_items,
    })

@login_required
def edit_artist_profile(request):
    if not request.user.is_artist:
        return redirect('home')

    artist = get_object_or_404(Artist, user=request.user)
    if request.method == 'POST':
        form = ArtistProfileForm(request.POST, request.FILES, instance=artist)
        if form.is_valid():
            form.save()
            return redirect('artist_dashboard')
    else:
        form = ArtistProfileForm(instance=artist)  # Pre-fill the form with existing data

    return render(request, 'catalogue/edit_artist_profile.html', {
        'form': form,
    })

def search_suggestions(request):
    query = request.GET.get('query', '')
    if query:
        # Fetch CraftItems and prefetch all related images
        items = CraftItem.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).prefetch_related(
            Prefetch('images', queryset=CraftItemImage.objects.all())
        )[:5]  # Limit to 5 CraftItems

        suggestions = []
        for item in items:
            # Get the first image associated with the CraftItem
            first_image = item.images.first()
            image_url = first_image.image.url if first_image else ''

            suggestions.append({
                'name': item.name,
                'image': image_url,  # Include image URL
                'price': str(item.price)  # Include price as a string
            })

        return JsonResponse({'suggestions': suggestions})
    return JsonResponse({'suggestions': []})

def save(self, *args, **kwargs):
    if self.is_unique and self.quantity != 1:
        raise ValueError("Quantity must be 1 for unique items.")
    super().save(*args, **kwargs)

def dashboard(request):
    # Sorting for categories - case insensitive
    category_name = request.GET.get('category', '') 
    categories = Category.objects.all()
    sort_by_category = request.GET.get("sort_by", "name")
    if sort_by_category == "name":
        categories = categories.order_by(Lower("name"))
    
    # Filtering for items
    category_filter = request.GET.get('category', '')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    sort_by_item = request.GET.get('sort_by', 'name')
    items_per_page = request.GET.get('items_per_page', 16)
    search_query = request.GET.get("search", "")  # Get search query from the GET request
    is_unique = request.GET.get('is_unique')
    is_sustainable = request.GET.get('is_sustainable')
    is_handmade = request.GET.get('is_handmade')

    items = CraftItem.objects.all()

    # Apply filters
    if category_name:
        items = items.filter(categories__name=category_name)

    if category_filter:
        items = items.filter(categories__name=category_filter)

    if price_min:
        items = items.filter(price__gte=price_min)
    if price_max:
        items = items.filter(price__lte=price_max)
    if is_unique:
        items = items.filter(is_unique=True)

    if is_sustainable:
        items = items.filter(is_sustainable=True)
    
    if is_handmade:
        items = items.filter(is_handmade=True)
    if search_query:
        items = items.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))

    # Sort items by the selected field
    if sort_by_item == "name":
        items = items.order_by(Lower("name"))  # Case-insensitive sorting
    else:
        items = items.order_by(sort_by_item)

    # Pagination
    items_per_page = request.GET.get("items_per_page", 16)  # Default 16 items per page
    paginator = Paginator(items, items_per_page)
    page_number = request.GET.get("page")
    page_items = paginator.get_page(page_number)

    context = {
        'categories': Category.objects.all(),
        'selected_category': category_name, 
        "items": page_items,  # Paginated items
        "search_query": search_query,  # Pass search query to template
        "total_items": items.count(), 
    }
    return render(request, "catalogue/dashboard.html", context)

def clear_cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    if cart:
        for cart_item in cart.cart_items.all():
            cart_item.item.available = True
            cart_item.item.save()

        cart.cart_items.all().delete()
        cart.save()

    return redirect('cart_detail')

def custom_login_view(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            # Add error message for invalid credentials
            messages.error(request, "Invalid username or password")
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'login.html', {
        'form': form,
        'errors': form.errors.get('__all__', [])  # Pass non-field errors explicitly
    })

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'  # Specify backend
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    
    return render(request, 'signup.html', {'form': form})

def artist_signup(request):
    if request.method == 'POST':
        form = ArtistSignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_artist = True
            user.save()

            # Create the artist profile
            artist = Artist(
                user=user,
                name=form.cleaned_data['name'],
                bio=form.cleaned_data['bio'],
                profile_picture=form.cleaned_data['profile_picture'],
                phone_number=form.cleaned_data['phone_number'],
                website=form.cleaned_data['website'],
                social_media_links=form.cleaned_data['social_media_links'],
                location=form.cleaned_data['location']
            )
            artist.save()

            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            return redirect('home')
        else:
            # Print form errors to the console
            print(form.errors)
    else:
        form = ArtistSignUpForm()
    return render(request, 'artist_signup.html', {'form': form})



def home(request):
    featured_item = CraftItem.objects.filter(featured=True, available=True).first()
    recent_items = CraftItem.objects.filter(available=True).order_by('-date_created')[:8]

    context = {
        'featured_item': featured_item,
        'recent_items': recent_items,
        'categories': Category.objects.all(),
    }
    return render(request, 'catalogue/home.html', context)



def catalogue(request):
    return render(request, 'catalogue/catalogue.html')

def category_items(request, category_name):
    category = get_object_or_404(Category, name=category_name)  # Get the category by name
    items = CraftItem.objects.filter(categories=category)  
    return render(request, 'catalogue/category_items.html', {'category': category, 'items': items})


def item_detail(request, item_name):
    item = get_object_or_404(CraftItem, name=item_name)
    return render(request, 'catalogue/item_detail.html', {'item': item})

def all_categories(request):
    categories = Category.objects.all()
    return render(request, "catalogue/all_categories.html", {"categories": categories})


def artist_list(request):
    artists = Artist.objects.all()
    return render(request, 'catalogue/artist_list.html', {'artists': artists})

def get_cart(request):
    if request.user.is_authenticated:
        # Use the cart from the user's profile (if logged in)
        cart = request.user.cart_set.last()
    else:
        # Use a session-based cart for logged-out users
        cart = request.session.get('cart', [])
    
    return cart

def artist_detail(request, artist_name):
    # Fetch the artist by name
    artist = get_object_or_404(Artist, name=artist_name)
    items = CraftItem.objects.filter(artist=artist)  # Filter items by the specific artist
    return render(request, 'catalogue/artist_detail.html', {'artist': artist, 'items': items})

def craft_item_list(request):
    return render(request, 'catalogue/craft_item_list.html')

def add_to_cart(request, item_id):
    if not request.user.is_authenticated:
        return redirect('login')

    item = get_object_or_404(CraftItem, id=item_id)

    if not item.available:
        messages.error(request, "This item is not available.")
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    cart, created = Cart.objects.get_or_create(user=request.user)

    remove_expired_unique_items(cart)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)

    if item.is_unique and not created:
        messages.error(request, "This unique item is already in your cart.")
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    if not created and not item.is_unique:
        cart_item.quantity += 1
        cart_item.save()

    # if item.is_unique:
    #     item.available = False
    #     item.save()

    return redirect(request.META.get('HTTP_REFERER', 'home'))



def remove_expired_unique_items(cart):
    expired_items = cart.cart_items.filter(item__is_unique=True, created_at__lte=timezone.now() - timezone.timedelta(minutes=30))
    for cart_item in expired_items:
        cart_item.item.available = True
        cart_item.item.save()
        cart_item.delete()

def remove_expired_items(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    cart, created = Cart.objects.get_or_create(user=request.user)
    remove_expired_unique_items(cart)

    return JsonResponse({"message": "Expired items removed"})

def update_cart_item_quantity(request, cart_item_id, action):
    try:
        cart_item = CartItem.objects.get(id=cart_item_id, cart__user=request.user)
        if action == 'increase':
            if cart_item.quantity < cart_item.item.quantity:
                cart_item.quantity += 1
                cart_item.save()
            else:
                return JsonResponse({'success': False, 'message': 'Maximum quantity reached'})
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                return JsonResponse({'success': False, 'message': 'Minimum quantity reached'})
        elif action == 'set':
            # Expect JSON with the new quantity
            try:
                data = json.loads(request.body)
                new_quantity = int(data.get('quantity', cart_item.quantity))
            except (ValueError, TypeError):
                return JsonResponse({'success': False, 'message': 'Invalid quantity'})
            
            if new_quantity < 1:
                return JsonResponse({'success': False, 'message': 'Invalid quantity'})
            
            max_qty = cart_item.item.quantity
            if new_quantity > max_qty:
                return JsonResponse({'success': False, 'message': 'Maximum quantity reached'})
            
            cart_item.quantity = new_quantity
            cart_item.save()
        else:
            return JsonResponse({'success': False, 'message': 'Invalid action'})
    
        return JsonResponse({'success': True})
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Item not found'}, status=404)

def cart_detail(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login if the user is not logged in
    
    # Proceed with rendering the cart details for logged-in users
    cart = request.user.cart_set.last()  # Assuming one cart per user
    
    # Check if the cart exists
    if cart:
        # Use the method total_price() to get the total price
        total_price = cart.total_price()  # Call the method with parentheses
        
        # Calculate fees and final total
        fees = total_price * Decimal('0.03')
        shipping = Decimal('5.00')  # Fixed shipping cost
        final_total = total_price + fees + shipping
        
        # Pass all the values to the template
        context = {
            'cart': cart,
            'total_price': total_price,
            'fees': fees,
            'final_total': final_total,
        }
    else:
        context = {'cart': None}
    
    return render(request, 'cart/cart_detail.html', context)


def logout_view(request):
    logout(request)
    return redirect('home') 

def checkout(request):
    if request.user.is_authenticated:
        cart = request.user.cart_set.last()  # Get the last cart associated with the user
        if cart:
            cart_items = cart.cart_items.all()  # Access the related CartItems
            total_price = cart.total_price()  # Calculate the total price of the cart
        else:
            cart_items = []
            total_price = 0
    else:
        cart_items = []
        total_price = 0

    return render(request, 'catalogue/checkout.html', {'cart_items': cart_items, 'total_price': total_price})

def complete_checkout(request):
    # Logic for completing the checkout, e.g., processing the order
    return render(request, 'catalogue/complete_checkout.html')



# @login_required
# def checkout(request):
#     if request.user.is_authenticated:
#         cart, created = Cart.objects.get_or_create(user=request.user)
#         cart.items.all().delete()  # Clear database cart
#     else:
#         request.session['cart'] = {}  # Clear session cart
#         request.session.modified = True

#     messages.success(request, "Checkout successful!")
#     return render(request, 'catalogue/thank_you.html')