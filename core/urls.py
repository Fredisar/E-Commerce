"""
Fichier urls.py pour l'application core
Définit toutes les routes (URLs) de l'application e-commerce
"""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # ========================
    # PAGES PUBLIQUES
    # ========================
    
    # Page d'accueil
     # Page d'accueil - ROUTE RACINE (IMPORTANT!)
    path('', views.home, name='home'),
    
    # Alternative pour /home/ (optionnel)
    path('home/', views.home, name='home_alt'),
    
    # Liste des produits
    path('products/', views.product_list, name='product_list'),
    path('products/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    
    # Détail d'un produit
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    
    # Recherche avancée
    path('search/', views.search_view, name='search_view'),
    
    # ========================
    # PANIER D'ACHAT
    # ========================
    
    # Vue du panier
    path('cart/', views.cart_view, name='cart'),
    
    # AJAX - Ajouter au panier (POST seulement)
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    
    # AJAX - Mettre à jour la quantité (POST seulement)
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    
    # AJAX - Supprimer du panier (POST seulement)
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # ========================
    # COMMANDE ET PAIEMENT
    # ========================
    
    # Processus de commande
    path('checkout/', views.checkout, name='checkout'),
    
    # Confirmation de commande (à créer plus tard)
    path('order/confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    
    # ========================
    # AUTHENTIFICATION UTILISATEUR
    # ========================
    
    # Connexion
    path('login/', views.user_login, name='login'),
    
    # Déconnexion
    path('logout/', views.user_logout, name='logout'),
    
    # Inscription
    path('register/', views.user_register, name='register'),
    
    # Mot de passe oublié (fonctionnalité future)
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='password_reset.html'), 
         name='password_reset'),
    
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), 
         name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), 
         name='password_reset_confirm'),
    
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), 
         name='password_reset_complete'),
    
    # ========================
    # PROFIL UTILISATEUR
    # ========================
    
    # Profil utilisateur
    path('profile/', views.user_profile, name='profile'),
    
    # Historique des commandes (à créer plus tard)
    path('profile/orders/', views.user_orders, name='user_orders'),
    
    # Détail d'une commande (à créer plus tard)
    path('profile/orders/<int:order_id>/', views.order_detail, name='order_detail'),
    
    # ========================
    # PAGES STATIQUES (optionnelles)
    # ========================
    
    # À propos
    path('about/', lambda request: views.static_page(request, 'about.html'), name='about'),
    
    # Contact
    path('contact/', lambda request: views.static_page(request, 'contact.html'), name='contact'),
    
    # Conditions générales
    path('terms/', lambda request: views.static_page(request, 'terms.html'), name='terms'),
    
    # Politique de confidentialité
    path('privacy/', lambda request: views.static_page(request, 'privacy.html'), name='privacy'),
    
    # FAQ
    path('faq/', lambda request: views.static_page(request, 'faq.html'), name='faq'),
]

# ========================
# VUE POUR LES PAGES STATIQUES
# ========================
def static_page(request, template_name):
    """Vue générique pour les pages statiques"""
    from django.shortcuts import render
    return render(request, template_name)

# Note: Pour utiliser cette vue, vous devrez créer les templates correspondants :
# about.html, contact.html, terms.html, privacy.html, faq.html