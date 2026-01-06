"""
Forms pour l'application e-commerce
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth import get_user_model  # ← IMPORTANT
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re
from .models import Order, UserProfile

# Utilisez get_user_model() pour obtenir votre modèle User personnalisé
User = get_user_model()  # ← CELA RETOURNERA core.User

class UserRegistrationForm(UserCreationForm):
    """Formulaire d'inscription utilisateur"""
    
    # Champs supplémentaires
    email = forms.EmailField(
        label=_("Email"),
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'votre@email.com'
        })
    )
    
    first_name = forms.CharField(
        label=_("Prénom"),
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prénom'
        })
    )
    
    last_name = forms.CharField(
        label=_("Nom"),
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom'
        })
    )
    
    phone = forms.CharField(
        label=_("Téléphone"),
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+33 1 23 45 67 89'
        })
    )
    
    newsletter_subscription = forms.BooleanField(
        label=_("S'abonner à la newsletter"),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    class Meta:
        model = User  # ← Utilise votre modèle User personnalisé
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password1', 'password2', 'phone', 'newsletter_subscription'
        ]
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom d\'utilisateur'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnalisation des messages d'aide
        self.fields['username'].help_text = _(
            'Requis. 150 caractères maximum. Lettres, chiffres et @/./+/-/_ uniquement.'
        )
        self.fields['password1'].help_text = _(
            'Votre mot de passe doit contenir au moins 8 caractères.'
        )
    
    def clean_email(self):
        """Validation de l'email"""
        email = self.cleaned_data.get('email')
        
        if email:
            # Vérifie si l'email existe déjà
            if User.objects.filter(email=email).exists():
                raise ValidationError(_("Cet email est déjà utilisé."))
            
            # Validation basique du format
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                raise ValidationError(_("Format d'email invalide."))
        
        return email
    
    def clean_phone(self):
        """Validation du téléphone"""
        phone = self.cleaned_data.get('phone', '')
        
        if phone:
            # Nettoyage du numéro
            phone = ''.join(filter(str.isdigit, phone))
            
            # Validation basique
            if len(phone) < 9 or len(phone) > 15:
                raise ValidationError(_("Numéro de téléphone invalide."))
        
        return phone

class UserLoginForm(AuthenticationForm):
    """Formulaire de connexion"""
    
    username = forms.CharField(
        label=_("Nom d'utilisateur ou Email"),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom d\'utilisateur ou email'
        })
    )
    
    password = forms.CharField(
        label=_("Mot de passe"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mot de passe'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Option pour permettre la connexion par email
        self.fields['username'].label = _("Nom d'utilisateur ou Email")

class UserProfileForm(forms.ModelForm):
    """Formulaire de mise à jour du profil"""
    
    first_name = forms.CharField(
        label=_("Prénom"),
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    last_name = forms.CharField(
        label=_("Nom"),
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = UserProfile  # Assurez-vous que c'est le bon modèle
        fields = [
            'first_name', 'last_name', 'phone', 'address',
            'city', 'postal_code', 'country', 'date_of_birth',
            'profile_picture', 'newsletter_subscription'
        ]
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'newsletter_subscription': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        # Récupérer l'utilisateur pour pré-remplir les champs
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user and self.instance:
            # Pré-remplir avec les données de l'utilisateur
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
    
    def save(self, commit=True):
        # Sauvegarder d'abord le profil
        profile = super().save(commit=False)
        
        # Mettre à jour l'utilisateur
        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            if commit:
                self.user.save()
        
        if commit:
            profile.save()
        
        return profile

class CheckoutForm(forms.ModelForm):
    """Formulaire de paiement"""
    
    class Meta:
        model = Order
        fields = [
            'shipping_address', 'billing_address',
            'payment_method', 'notes'
        ]
        widgets = {
            'shipping_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Adresse de livraison complète'
            }),
            'billing_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Adresse de facturation'
            }),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Notes supplémentaires pour la livraison...'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Si l'adresse de facturation n'est pas remplie, utiliser l'adresse de livraison
        if not cleaned_data.get('billing_address'):
            cleaned_data['billing_address'] = cleaned_data.get('shipping_address', '')
        
        return cleaned_data

class PasswordChangeCustomForm(PasswordChangeForm):
    """Formulaire personnalisé de changement de mot de passe"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnalisation des champs
        for field_name in ['old_password', 'new_password1', 'new_password2']:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})