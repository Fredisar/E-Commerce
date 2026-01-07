"""
Script pour créer des données de test pour l'e-commerce
"""
import os
import django
from datetime import datetime, timedelta
import random
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_project.settings')
django.setup()

from core.models import Category, Product, ProductImage
from django.core.files.base import ContentFile

# Nettoyage (optionnel - attention supprime les données existantes)
# ProductImage.objects.all().delete()
# Product.objects.all().delete()
# Category.objects.all().delete()

# Création des catégories
categories_data = [
    {
        'name': 'Smartphones',
        'slug': 'smartphones',
        'description': 'Les derniers smartphones et téléphones mobiles',
    },
    {
        'name': 'Ordinateurs Portables',
        'slug': 'ordinateurs-portables',
        'description': 'PC portables, ultrabooks et convertibles',
    },
    {
        'name': 'Tablettes',
        'slug': 'tablettes',
        'description': 'Tablettes tactiles et iPad',
    },
    {
        'name': 'Écouteurs & Casques',
        'slug': 'ecouteurs-casques',
        'description': 'Casques audio, écouteurs et accessoires audio',
    },
    {
        'name': 'Montres Connectées',
        'slug': 'montres-connectees',
        'description': 'Smartwatches et bracelets connectés',
    },
    {
        'name': 'Gaming',
        'slug': 'gaming',
        'description': 'Console de jeux, PC gaming et accessoires',
    },
    {
        'name': 'Accessoires',
        'slug': 'accessoires',
        'description': 'Accessoires et périphériques',
    },
]

categories = {}
for cat_data in categories_data:
    cat, created = Category.objects.get_or_create(
        slug=cat_data['slug'],
        defaults=cat_data
    )
    categories[cat.slug] = cat
    print(f"✅ Catégorie: {cat.name}")

# Données des produits
products_data = [
    # Smartphones
    {
        'name': 'iPhone 15 Pro Max',
        'slug': 'iphone-15-pro-max',
        'description': 'iPhone 15 Pro Max avec écran Super Retina XDR, processeur A17 Pro et caméra 48MP.',
        'price': Decimal('1299.99'),
        'discount_price': Decimal('1199.99'),
        'category': categories['smartphones'],
        'brand': 'Apple',
        'stock': 50,
        'weight': Decimal('0.221'),
        'dimensions': '160.9 x 77.8 x 8.3 mm',
        'meta_title': 'iPhone 15 Pro Max - Le meilleur smartphone Apple',
        'meta_description': 'Achetez l\'iPhone 15 Pro Max avec les dernières fonctionnalités Apple',
    },
    {
        'name': 'Samsung Galaxy S24 Ultra',
        'slug': 'samsung-galaxy-s24-ultra',
        'description': 'Samsung Galaxy S24 Ultra avec S-Pen, écran Dynamic AMOLED 2X et caméra 200MP.',
        'price': Decimal('1349.99'),
        'discount_price': Decimal('1249.99'),
        'category': categories['smartphones'],
        'brand': 'Samsung',
        'stock': 35,
        'weight': Decimal('0.233'),
        'dimensions': '162.3 x 79.0 x 8.6 mm',
    },
    {
        'name': 'Google Pixel 8 Pro',
        'slug': 'google-pixel-8-pro',
        'description': 'Pixel 8 Pro avec Google Tensor G3, Android pur et caméra professionnelle.',
        'price': Decimal('999.99'),
        'category': categories['smartphones'],
        'brand': 'Google',
        'stock': 40,
        'weight': Decimal('0.213'),
        'dimensions': '162.6 x 76.5 x 8.8 mm',
    },
    
    # Ordinateurs Portables
    {
        'name': 'MacBook Pro 16" M3 Max',
        'slug': 'macbook-pro-16-m3-max',
        'description': 'MacBook Pro 16 pouces avec puce M3 Max, 32GB RAM, 1TB SSD.',
        'price': Decimal('3499.99'),
        'discount_price': Decimal('3299.99'),
        'category': categories['ordinateurs-portables'],
        'brand': 'Apple',
        'stock': 20,
        'weight': Decimal('2.15'),
        'dimensions': '35.57 x 24.81 x 1.68 cm',
    },
    {
        'name': 'Dell XPS 15',
        'slug': 'dell-xps-15',
        'description': 'Dell XPS 15 avec Intel Core i9, RTX 4070, 32GB RAM, écran 4K OLED.',
        'price': Decimal('2499.99'),
        'category': categories['ordinateurs-portables'],
        'brand': 'Dell',
        'stock': 25,
        'weight': Decimal('1.86'),
        'dimensions': '34.4 x 23.0 x 1.8 cm',
    },
    
    # Tablettes
    {
        'name': 'iPad Pro 12.9" M2',
        'slug': 'ipad-pro-12-9-m2',
        'description': 'iPad Pro 12.9 pouces avec puce M2, écran Liquid Retina XDR.',
        'price': Decimal('1299.99'),
        'discount_price': Decimal('1199.99'),
        'category': categories['tablettes'],
        'brand': 'Apple',
        'stock': 30,
        'weight': Decimal('0.682'),
        'dimensions': '280.6 x 214.9 x 6.4 mm',
    },
    
    # Casques
    {
        'name': 'Sony WH-1000XM5',
        'slug': 'sony-wh-1000xm5',
        'description': 'Casque sans fil à réduction de bruit active.',
        'price': Decimal('349.99'),
        'discount_price': Decimal('299.99'),
        'category': categories['ecouteurs-casques'],
        'brand': 'Sony',
        'stock': 60,
        'weight': Decimal('0.250'),
        'dimensions': '20 x 18 x 7 cm',
    },
    
    # Montres connectées
    {
        'name': 'Apple Watch Ultra 2',
        'slug': 'apple-watch-ultra-2',
        'description': 'Montre connectée pour sports extrêmes, écran 49mm.',
        'price': Decimal('899.99'),
        'category': categories['montres-connectees'],
        'brand': 'Apple',
        'stock': 45,
        'weight': Decimal('0.061'),
        'dimensions': '49 x 44 x 14.4 mm',
    },
    
    # Gaming
    {
        'name': 'PlayStation 5',
        'slug': 'playstation-5',
        'description': 'Console PlayStation 5 avec lecteur Blu-ray, 1TB SSD.',
        'price': Decimal('499.99'),
        'discount_price': Decimal('449.99'),
        'category': categories['gaming'],
        'brand': 'Sony',
        'stock': 15,
        'weight': Decimal('4.5'),
        'dimensions': '39 x 26 x 10.4 cm',
    },
    
    # Accessoires
    {
        'name': 'Chargeur MagSafe Apple',
        'slug': 'chargeur-magsafe-apple',
        'description': 'Chargeur sans fil MagSafe 15W pour iPhone.',
        'price': Decimal('39.99'),
        'category': categories['accessoires'],
        'brand': 'Apple',
        'stock': 100,
        'weight': Decimal('0.050'),
        'dimensions': '6 x 6 x 1 cm',
    },
]

# Création des produits
for prod_data in products_data:
    product, created = Product.objects.get_or_create(
        slug=prod_data['slug'],
        defaults={
            'name': prod_data['name'],
            'description': prod_data['description'],
            'price': prod_data['price'],
            'discount_price': prod_data.get('discount_price'),
            'category': prod_data['category'],
            'brand': prod_data.get('brand', ''),
            'stock': prod_data.get('stock', 10),
            'is_available': True,
            'weight': prod_data.get('weight'),
            'dimensions': prod_data.get('dimensions', ''),
            'meta_title': prod_data.get('meta_title', ''),
            'meta_description': prod_data.get('meta_description', ''),
        }
    )
    
    if created:
        print(f"✅ Produit créé: {product.name} - {product.price}€")
    else:
        print(f"⚠️  Produit existant: {product.name}")

print("\n🎉 Données de test créées avec succès !")
print(f"Total catégories: {Category.objects.count()}")
print(f"Total produits: {Product.objects.count()}")
