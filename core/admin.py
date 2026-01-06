from django.contrib import admin

# Register your models here.
"""
Administration Django pour l'application e-commerce
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import (
    User, Category, Product, ProductImage, 
    Cart, CartItem, Order, OrderItem, UserProfile
)


# ==================== USER ADMIN ====================

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Administration pour le modèle User personnalisé"""
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )


# ==================== CATEGORY ADMIN ====================

class ProductInline(admin.TabularInline):
    """Inline pour afficher les produits d'une catégorie"""
    model = Product
    extra = 0
    fields = ('name', 'price', 'stock', 'is_available')
    readonly_fields = ('created_at',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Administration pour les catégories"""
    
    list_display = ('name', 'slug', 'product_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductInline]
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = _('Nombre de produits')


# ==================== PRODUCT ADMIN ====================

class ProductImageInline(admin.TabularInline):
    """Inline pour les images supplémentaires du produit"""
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'is_featured')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Administration pour les produits"""
    
    list_display = ('name', 'category', 'price', 'discount_price', 'stock', 'is_available', 'created_at')
    list_filter = ('category', 'is_available', 'created_at')
    search_fields = ('name', 'description', 'brand')
    list_editable = ('price', 'stock', 'is_available')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ProductImageInline]
    
    fieldsets = (
        (_('Informations de base'), {
            'fields': ('name', 'slug', 'description', 'category', 'image')
        }),
        (_('Prix et stock'), {
            'fields': ('price', 'discount_price', 'stock', 'is_available')
        }),
        (_('Caractéristiques'), {
            'fields': ('brand', 'weight', 'dimensions'),
            'classes': ('collapse',)
        }),
        (_('Référencement'), {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def final_price(self, obj):
        return obj.final_price
    final_price.short_description = _('Prix final')
    
    def has_discount(self, obj):
        return obj.has_discount
    has_discount.short_description = _('En promo')
    has_discount.boolean = True


# ==================== CART ADMIN ====================

class CartItemInline(admin.TabularInline):
    """Inline pour les articles du panier"""
    model = CartItem
    extra = 0
    fields = ('product', 'quantity', 'total_price_display')
    readonly_fields = ('total_price_display',)
    
    def total_price_display(self, obj):
        return f"{obj.total_price} €"
    total_price_display.short_description = _('Prix total')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Administration pour les paniers"""
    
    list_display = ('id', 'user_display', 'session_key', 'total_items', 'total_price_display', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'session_key')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CartItemInline]
    
    fieldsets = (
        (None, {
            'fields': ('user', 'session_key')
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_display(self, obj):
        return obj.user.username if obj.user else _('Anonyme')
    user_display.short_description = _('Utilisateur')
    
    def total_price_display(self, obj):
        return f"{obj.total_price} €"
    total_price_display.short_description = _('Total panier')
    
    def total_items(self, obj):
        return obj.total_items
    total_items.short_description = _('Articles')


# ==================== ORDER ADMIN ====================

class OrderItemInline(admin.TabularInline):
    """Inline pour les articles de commande"""
    model = OrderItem
    extra = 0
    fields = ('product', 'quantity', 'price', 'total_price_display')
    readonly_fields = ('total_price_display',)
    
    def total_price_display(self, obj):
        return f"{obj.total_price} €"
    total_price_display.short_description = _('Sous-total')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Administration pour les commandes"""
    
    list_display = ('order_number', 'user', 'status', 'total_amount', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'user__username', 'user__email')
    list_editable = ('status',)
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    
    fieldsets = (
        (_('Informations commande'), {
            'fields': ('order_number', 'user', 'status', 'total_amount', 'payment_method')
        }),
        (_('Adresses'), {
            'fields': ('shipping_address', 'billing_address')
        }),
        (_('Notes'), {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']
    
    def mark_as_processing(self, request, queryset):
        queryset.update(status='processing')
        self.message_user(request, _('Commandes marquées comme "En traitement".'))
    mark_as_processing.short_description = _('Marquer comme "En traitement"')
    
    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')
        self.message_user(request, _('Commandes marquées comme "Expédiées".'))
    mark_as_shipped.short_description = _('Marquer comme "Expédiées"')
    
    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')
        self.message_user(request, _('Commandes marquées comme "Livrées".'))
    mark_as_delivered.short_description = _('Marquer comme "Livrées"')
    
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
        self.message_user(request, _('Commandes marquées comme "Annulées".'))
    mark_as_cancelled.short_description = _('Marquer comme "Annulées"')


# ==================== USER PROFILE ADMIN ====================

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Administration pour les profils utilisateurs"""
    
    list_display = ('user', 'phone', 'city', 'country', 'newsletter_subscription')
    list_filter = ('country', 'newsletter_subscription', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone', 'city')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Informations utilisateur'), {
            'fields': ('user',)
        }),
        (_('Contact'), {
            'fields': ('phone', 'address', 'city', 'postal_code', 'country')
        }),
        (_('Informations personnelles'), {
            'fields': ('profile_picture', 'date_of_birth'),
            'classes': ('collapse',)
        }),
        (_('Préférences'), {
            'fields': ('newsletter_subscription',),
            'classes': ('collapse',)
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# ==================== OTHER MODELS ====================

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Administration pour les images de produits"""
    
    list_display = ('product', 'image', 'is_featured', 'created_at')
    list_filter = ('is_featured', 'created_at')
    search_fields = ('product__name', 'alt_text')
    list_editable = ('is_featured',)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Administration pour les articles du panier"""
    
    list_display = ('cart', 'product', 'quantity', 'total_price_display', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('cart__session_key', 'product__name')
    
    def total_price_display(self, obj):
        return f"{obj.total_price} €"
    total_price_display.short_description = _('Prix total')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Administration pour les articles de commande"""
    
    list_display = ('order', 'product', 'quantity', 'price', 'total_price_display', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('order__order_number', 'product__name')
    
    def total_price_display(self, obj):
        return f"{obj.total_price} €"
    total_price_display.short_description = _('Sous-total')


# ==================== ADMIN SITE CONFIGURATION ====================

# Personnalisation de l'interface d'administration
admin.site.site_header = _('Administration Nexus Shop')
admin.site.site_title = _('Nexus Shop Admin')
admin.site.index_title = _('Tableau de bord')

# Organisation des modèles dans l'admin
admin.site.index_template = 'admin/custom_index.html'