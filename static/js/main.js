/**
 * Script principal pour Nexus Shop
 * Gestion dynamique du panier et effets UI
 */

// Dans votre JavaScript
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

fetch('/register/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
    },
    body: JSON.stringify(data)
});


$(document).ready(function() {
    
    // Gestion du panier - Ajouter au panier
    $('.add-to-cart').on('click', function(e) {
        e.preventDefault();
        const productId = $(this).data('product-id');
        const $button = $(this);
        
        // Animation du bouton
        $button.html('<i class="fas fa-spinner fa-spin"></i>');
        $button.prop('disabled', true);
        
        $.ajax({
            url: '/cart/add/' + productId + '/',
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            success: function(response) {
                if (response.success) {
                    // Mettre à jour le compteur du panier
                    updateCartCount(response.cart_total);
                    
                    // Notification
                    showNotification(response.message, 'success');
                    
                    // Rétablir le bouton
                    setTimeout(() => {
                        $button.html('<i class="fas fa-cart-plus me-2"></i>Ajouter au panier');
                        $button.prop('disabled', false);
                    }, 1000);
                }
            },
            error: function() {
                showNotification('Erreur lors de l\'ajout au panier', 'error');
                $button.html('<i class="fas fa-cart-plus me-2"></i>Ajouter au panier');
                $button.prop('disabled', false);
            }
        });
    });
    
    // Gestion du panier - Mettre à jour la quantité
    $('.update-quantity').on('change', function() {
        const itemId = $(this).data('item-id');
        const quantity = $(this).val();
        const $row = $(this).closest('.cart-item');
        
        $.ajax({
            url: '/cart/update/' + itemId + '/',
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            contentType: 'application/json',
            data: JSON.stringify({ quantity: quantity }),
            success: function(response) {
                if (response.success) {
                    if (response.deleted) {
                        $row.fadeOut(300, function() {
                            $(this).remove();
                            updateCartTotal(response.cart_total);
                        });
                    } else {
                        // Mettre à jour les totaux
                        $row.find('.item-total').text('€' + response.total_price.toFixed(2));
                        updateCartTotal(response.cart_total);
                    }
                }
            }
        });
    });
    
    // Gestion du panier - Supprimer un article
    $('.remove-from-cart').on('click', function() {
        const itemId = $(this).data('item-id');
        const $row = $(this).closest('.cart-item');
        
        if (confirm('Voulez-vous vraiment supprimer cet article du panier ?')) {
            $.ajax({
                url: '/cart/remove/' + itemId + '/',
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                success: function(response) {
                    if (response.success) {
                        $row.fadeOut(300, function() {
                            $(this).remove();
                            updateCartTotal(response.cart_total);
                            showNotification('Article supprimé du panier', 'info');
                        });
                    }
                }
            });
        }
    });
    
    // Fonction pour mettre à jour le compteur du panier
    function updateCartCount(count) {
        const $cartBadge = $('.cart-badge');
        
        if (count > 0) {
            if ($cartBadge.length) {
                $cartBadge.text(count);
            } else {
                // Créer le badge s'il n'existe pas
                $('.fa-shopping-cart').after(
                    `<span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger cart-badge">
                        ${count}
                    </span>`
                );
            }
        } else {
            $cartBadge.remove();
        }
    }
    
    // Fonction pour mettre à jour le total du panier
    function updateCartTotal(total) {
        $('.cart-total').text('€' + total.toFixed(2));
        
        // Mettre à jour le compteur d'articles si nécessaire
        let itemCount = 0;
        $('.cart-item').each(function() {
            itemCount += parseInt($(this).find('.quantity').val());
        });
        updateCartCount(itemCount);
    }
    
    // Fonction pour afficher des notifications
    function showNotification(message, type = 'info') {
        // Créer l'élément de notification
        const $notification = $(`
            <div class="notification alert alert-${type} alert-dismissible fade show" 
                 role="alert" style="position: fixed; top: 80px; right: 20px; z-index: 9999;">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `);
        
        // Ajouter au DOM
        $('body').append($notification);
        
        // Supprimer automatiquement après 3 secondes
        setTimeout(() => {
            $notification.alert('close');
        }, 3000);
    }
    
    // Effet de survol sur les cartes produits
    $('.product-card').on('mouseenter', function() {
        $(this).addClass('shadow-lg');
    }).on('mouseleave', function() {
        $(this).removeClass('shadow-lg');
    });
    
    // Gestion de la recherche en temps réel (optionnel)
    let searchTimer;
    $('#search-input').on('input', function() {
        clearTimeout(searchTimer);
        const query = $(this).val();
        
        if (query.length >= 3) {
            searchTimer = setTimeout(() => {
                performLiveSearch(query);
            }, 500);
        }
    });
    
    // Barre de progression pour le chargement des images
    $('.product-img').on('load', function() {
        $(this).parent().addClass('loaded');
    });
    
    // Gestion des filtres
    $('.filter-option').on('change', function() {
        $(this).closest('form').submit();
    });
    
    // Animation des chiffres (pour les statistiques)
    $('.counter').each(function() {
        $(this).prop('Counter', 0).animate({
            Counter: $(this).text()
        }, {
            duration: 2000,
            easing: 'swing',
            step: function(now) {
                $(this).text(Math.ceil(now));
            }
        });
    });
    
    // Fonction utilitaire pour récupérer le token CSRF
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});