"""
Processeurs de contexte pour l'application e-commerce
"""
# core/context_processors.py (créez ce fichier s'il n'existe pas)
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from .models import User, Product, Order
from .views import get_or_create_cart

def cart_item_count(request):
    """
    Ajoute le nombre d'articles dans le panier au contexte
    Accessible dans tous les templates
    """
    if request.user.is_authenticated or request.session.session_key:
        cart = get_or_create_cart(request)
        return {'cart_item_count': cart.total_items}
    return {'cart_item_count': 0}




def admin_stats(request):
    """Contexte pour les statistiques de l'admin"""
    if request.path.startswith('/admin/'):
        # Statistiques utilisateurs
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        staff_users = User.objects.filter(is_staff=True).count()
        
        # Nouveaux utilisateurs (7 derniers jours)
        seven_days_ago = timezone.now() - timedelta(days=7)
        new_users_7d = User.objects.filter(date_joined__gte=seven_days_ago).count()
        
        # 5 derniers utilisateurs
        latest_users = User.objects.order_by('-date_joined')[:5]
        
        # Statistiques produits
        product_count = Product.objects.count()
        
        # Statistiques commandes
        order_count = Order.objects.count()
        revenue = Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0
        
        return {
            'user_count': total_users,
            'active_users': active_users,
            'staff_users': staff_users,
            'total_users': total_users,
            'new_users_7d': new_users_7d,
            'latest_users': latest_users,
            'product_count': product_count,
            'order_count': order_count,
            'revenue': revenue,
        }
    return {}