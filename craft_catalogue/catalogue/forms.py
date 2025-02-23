from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import CustomUser, CraftItem, CraftItemImage, Category, Artist

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

        # forms.py
class ArtistSignUpForm(UserCreationForm):
    # Additional fields for artists
    name = forms.CharField(max_length=255)
    bio = forms.CharField(widget=forms.Textarea)
    profile_picture = forms.ImageField(required=False)
    phone_number = forms.CharField(max_length=15, required=False)
    website = forms.URLField(required=False)
    social_media_links = forms.JSONField(required=False)
    location = forms.CharField(max_length=255, required=False)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

class ArtistProfileForm(forms.ModelForm):
    class Meta:
        model = Artist
        fields = ['name', 'bio', 'profile_picture', 'email', 'phone_number', 'website', 'social_media_links', 'location']

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="Username or Email")


class CraftItemForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = CraftItem
        fields = [
            'name', 'description', 'categories', 'price', 'available', 'dimensions',
            'is_unique', 'quantity', 'is_sustainable', 'is_handmade'
        ]
        
class CraftItemImageForm(forms.ModelForm):
    class Meta:
        model = CraftItemImage
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'required': False}),
        }