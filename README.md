# 🚀 Nexus Shop - Plateforme E-commerce Futuriste

[![Django Version](https://img.shields.io/badge/Django-5.2.8-green.svg)](https://www.djangoproject.com/)
[![Python Version](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()

Nexus Shop est une plateforme e-commerce moderne développée avec Django, offrant une expérience d'achat futuriste avec des fonctionnalités avancées et une interface utilisateur innovante.

## ✨ Fonctionnalités

### 🛍️ Fonctionnalités principales
- ✅ **Catalogue produits complet** avec catégories et filtres
- ✅ **Système de panier persistant** (sessions + utilisateurs)
- ✅ **Recherche avancée** avec filtres multicritères
- ✅ **Gestion des promotions** et réductions dynamiques
- ✅ **Interface responsive** et design futuriste
- ✅ **Système d'authentification** sécurisé
- ✅ **Backend administrateur** Django complet

### 🔧 Technologies utilisées
- **Backend** : Django 5.2.8, Python 3.13
- **Frontend** : HTML5, CSS3, JavaScript, Bootstrap 5.3
- **Base de données** : SQLite (dev) / PostgreSQL (prod)
- **Authentification** : Django Auth avec modèle personnalisé
- **Media** : Django Storage pour les images produits
- **Développement** : Git, Virtualenv, pip

## 🚀 Installation

### Prérequis
- Python 3.13 ou supérieur
- pip (gestionnaire de paquets Python)
- Git

### Installation rapide

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/votreusername/nexus-shop.git
   cd nexus-shop
   ```
2. **Créer un environnement virtuel**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    # ou
    venv\Scripts\activate  # Windows
    ```
3. **Installer les dépendances**
    ```bash
    pip install -r requirements.txt
    ```
4. **Configurer la base de données**
    ```bash
    python manage.py migrate
    ```
5. **Créer un superutilisateur**
   ```bash
   python manage.py createsuperuser
   ```
6. **Lancer le serveur de développement**
   ```bash
   python manage.py runserver
   ```
7. **Accéder à l'application**
   - Site : http://127.0.0.1:8000
   - Admin : http://127.0.0.1:8000/admin

## **📁 Structure du projet**
nexus-shop/
├── core/                    # Application principale
│   ├── models.py           # Modèles de données
│   ├── views.py            # Vues et logique métier
│   ├── urls.py             # Routes de l'application
│   └── templates/          # Templates HTML
├── static/                 # Fichiers statiques
│   ├── css/style.css      # Styles personnalisés
│   └── js/main.js         # JavaScript
├── media/                  # Fichiers uploadés
├── requirements.txt        # Dépendances Python
└── manage.py              # Script de gestion Django
