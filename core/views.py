"""
Vues pour l'application e-commerce
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.db.models.query_utils import Q
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
import json
from django.db import transaction
import logging
from .models import User  # User personnalisé
from django.db import models

# Import des modèles CORRECTS
from .models import Product, Category, Cart, CartItem, Order
# IMPORTANT: On utilise UserProfile, pas Customer (si vous avez gardé UserProfile)
# Si vous avez renommé en Customer, changez ici
from .models import UserProfile

# Import des forms CORRECTS
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, CheckoutForm, PasswordChangeCustomForm

# Configuration du logging
logger = logging.getLogger(__name__)

def home(request):
    """Vue pour la page d'accueil"""
    featured_products = Product.objects.filter(is_available=True).order_by('-created_at')[:8]
    discounted_products = Product.objects.filter(
        discount_price__isnull=False, 
        is_available=True
    ).order_by('?')[:4]
    
    categories = Category.objects.all()[:6]
    
    context = {
        'featured_products': featured_products,
        'discounted_products': discounted_products,
        'categories': categories,
    }
    return render(request, 'home.html', context)

def product_list(request, category_slug=None):
    """Vue pour la liste des produits"""
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(is_available=True)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    # Recherche
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )
    
    # Filtrage par prix
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Tri
    sort_by = request.GET.get('sort_by', 'newest')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:  # newest
        products = products.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'categories': categories,
        'products': page_obj,
        'sort_by': sort_by,
    }
    return render(request, 'product_list.html', context)

def product_detail(request, slug):
    """Vue pour les détails d'un produit"""
    product = get_object_or_404(Product, slug=slug, is_available=True)
    related_products = Product.objects.filter(
        category=product.category, 
        is_available=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'product_detail.html', context)

def get_or_create_cart(request):
    """
    Récupère ou crée un panier pour l'utilisateur
    Gère à la fois les utilisateurs authentifiés et les visiteurs anonymes
    """
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        cart, created = Cart.objects.get_or_create(
            session_key=session_key,
            user=None
        )
    return cart

def cart_view(request):
    """Vue pour afficher le panier"""
    cart = get_or_create_cart(request)
    
    context = {
        'cart': cart,
    }
    return render(request, 'cart.html', context)

@require_POST
def add_to_cart(request, product_id):
    """Ajoute un produit au panier (AJAX)"""
    product = get_object_or_404(Product, id=product_id, is_available=True)
    cart = get_or_create_cart(request)
    
    # Vérifie si le produit est déjà dans le panier
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    return JsonResponse({
        'success': True,
        'message': f'{product.name} ajouté au panier',
        'cart_total': cart.total_items,
    })

@require_POST
def update_cart_item(request, item_id):
    """Met à jour la quantité d'un article dans le panier (AJAX)"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    
    try:
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            
            return JsonResponse({
                'success': True,
                'total_price': cart_item.total_price,
                'cart_total': cart_item.cart.total_price,
            })
        else:
            cart_item.delete()
            return JsonResponse({
                'success': True,
                'deleted': True,
                'cart_total': cart_item.cart.total_price,
            })
    except (ValueError, json.JSONDecodeError):
        return JsonResponse({'success': False, 'error': 'Données invalides'})

@require_POST
def remove_from_cart(request, item_id):
    """Supprime un article du panier (AJAX)"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    
    return JsonResponse({
        'success': True,
        'cart_total': cart_item.cart.total_price,
    })

@login_required
def checkout(request):
    """Vue pour le processus de paiement"""
    cart = get_or_create_cart(request)
    
    if cart.total_items == 0:
        messages.warning(request, "Votre panier est vide")
        return redirect('cart')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Créer la commande
            order = form.save(commit=False)
            order.user = request.user
            order.total_amount = cart.total_price
            order.save()
            
            # Créer les articles de commande
            for cart_item in cart.items.all():
                order_item = order.items.create(
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.final_price
                )
            
            # Vider le panier
            cart.items.all().delete()
            
            messages.success(request, "Votre commande a été passée avec succès!")
            return redirect('order_confirmation', order_id=order.id)
    else:
        # Pré-remplir le formulaire avec les informations du profil
        try:
            profile = request.user.profile  # Ou request.user.customer_profile si vous avez changé
            initial_data = {
                'shipping_address': profile.address,
                'billing_address': profile.address,
                'city': profile.city,
                'postal_code': profile.postal_code,
                'country': profile.country,
            }
        except:
            initial_data = {}
        
        form = CheckoutForm(initial=initial_data)
    
    context = {
        'cart': cart,
        'form': form,
    }
    return render(request, 'checkout.html', context)

def user_login(request):
    """
    Vue pour la connexion utilisateur
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)  # Utilise AuthenticationForm Django
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Authentifier l'utilisateur
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # Connexion réussie
                login(request, user)
                
                # Message de bienvenue
                messages.success(request, f"Bon retour {user.first_name or user.username} !")
                
                # Redirection
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})

def user_register(request):
    """
    Vue pour l'inscription utilisateur avec transaction PostgreSQL
    """
    if request.user.is_authenticated:
        messages.info(request, "Vous êtes déjà connecté.")
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        
        if form.is_valid():
            try:
                # Commencer une transaction pour garantir l'intégrité des données
                with transaction.atomic():
                    # 1. Créer l'utilisateur Django (table auth_user)
                    user = User.objects.create_user(
                        username=form.cleaned_data['username'],
                        email=form.cleaned_data['email'],
                        password=form.cleaned_data['password1'],
                        first_name=form.cleaned_data.get('first_name', ''),
                        last_name=form.cleaned_data.get('last_name', '')
                    )
                    
                    # 2. Créer le profil utilisateur (UserProfile ou Customer)
                    # MODIFIEZ ICI si vous avez changé le nom du modèle
                    UserProfile.objects.create(
                        user=user,
                        phone=form.cleaned_data.get('phone', ''),
                        newsletter_subscription=form.cleaned_data.get('newsletter_subscription', True)
                    )
                    
                    # 3. Connecter automatiquement l'utilisateur
                    login(request, user)
                    
                    # 4. Log de l'inscription
                    logger.info(f"Nouvel utilisateur inscrit: {user.username} ({user.email})")
                    
                    # 5. Message de succès
                    messages.success(
                        request, 
                        f"Bienvenue {user.first_name or user.username} ! Votre compte a été créé avec succès."
                    )
                    
                    # 6. Rediriger vers la page d'accueil
                    return redirect('home')
                    
            except Exception as e:
                # En cas d'erreur, la transaction est annulée automatiquement
                logger.error(f"Erreur lors de l'inscription: {str(e)}")
                messages.error(
                    request,
                    "Une erreur est survenue lors de la création de votre compte. "
                    "Veuillez réessayer."
                )
        else:
            # Afficher les erreurs de validation
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserRegistrationForm()
    
    return render(request, 'register.html', {'form': form})

def user_logout(request):
    """Vue pour la déconnexion"""
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        messages.info(request, "Vous avez été déconnecté avec succès.")
        logger.info(f"Utilisateur déconnecté: {username}")
    
    return redirect('home')

@login_required
def user_profile(request):
    """
    Vue pour la gestion du profil utilisateur
    """
    # MODIFIEZ ICI si vous avez changé le nom du modèle
    try:
        profile = request.user.profile  # Ou request.user.customer_profile
    except:
        # Créer un profil si inexistant
        profile = UserProfile.objects.create(user=request.user)  # Ou Customer.objects.create
    
    # Récupérer les commandes de l'utilisateur
    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # Calculer les dépenses totales
    total_spent = Order.objects.filter(
        user=request.user, 
        status='delivered'
    ).aggregate(total=models.Sum('total_amount'))['total'] or 0
    
    if request.method == 'POST':
        # Vérifier quel formulaire est soumis
        if 'update_profile' in request.POST:
            form = UserProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
            
            if form.is_valid():
                try:
                    with transaction.atomic():
                        # Mettre à jour l'utilisateur
                        request.user.first_name = form.cleaned_data.get('first_name', '')
                        request.user.last_name = form.cleaned_data.get('last_name', '')
                        request.user.save()
                        
                        # Mettre à jour le profil
                        form.save()
                        
                        messages.success(request, "Votre profil a été mis à jour avec succès.")
                        logger.info(f"Profil mis à jour: {request.user.username}")
                        
                except Exception as e:
                    logger.error(f"Erreur mise à jour profil: {str(e)}")
                    messages.error(request, "Une erreur est survenue lors de la mise à jour.")
        
        elif 'change_password' in request.POST:
            password_form = PasswordChangeCustomForm(request.user, request.POST)
            
            if password_form.is_valid():
                try:
                    password_form.save()
                    messages.success(request, "Votre mot de passe a été changé avec succès.")
                    logger.info(f"Mot de passe changé: {request.user.username}")
                except Exception as e:
                    logger.error(f"Erreur changement mot de passe: {str(e)}")
                    messages.error(request, "Une erreur est survenue.")
    else:
        form = UserProfileForm(instance=profile, user=request.user)
        password_form = PasswordChangeCustomForm(request.user)
    
    context = {
        'form': form,
        'password_form': password_form,
        'orders': orders,
        'total_spent': total_spent
    }
    
    return render(request, 'profile.html', context)

def search_view(request):
    """Vue pour la recherche avancée"""
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    
    products = Product.objects.filter(is_available=True)
    
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )
    
    if category:
        products = products.filter(category__slug=category)
    
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass
    
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'selected_category': category,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'search.html', context)

@login_required
def order_confirmation(request, order_id):
    """Vue pour la confirmation de commande"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
    }
    return render(request, 'order_confirmation.html', context)

@login_required
def user_orders(request):
    """Vue pour l'historique des commandes"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'user_orders.html', context)

@login_required
def order_detail(request, order_id):
    """Vue pour le détail d'une commande"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
    }
    return render(request, 'order_detail.html', context)

def static_page(request, template_name):
    """Vue générique pour les pages statiques"""
    return render(request, template_name)

def password_reset_request(request):
    """Vue pour la réinitialisation du mot de passe"""
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    # Envoyer l'email de réinitialisation
                    subject = "Réinitialisation du mot de passe - Nexus Shop"
                    email_template_name = "password_reset_email.txt"
                    context = {
                        'email': user.email,
                        'domain': request.get_host(),
                        'site_name': 'Nexus Shop',
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'user': user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    # Ici vous enverriez l'email normalement
                    messages.info(request, "Un email de réinitialisation a été envoyé.")
                    return redirect("password_reset_done")
    else:
        form = PasswordResetForm()
    
    return render(request, 'password_reset.html', {'form': form})