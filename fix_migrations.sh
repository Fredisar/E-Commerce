#!/bin/bash
echo "Correction des migrations Django..."

# Fake les migrations de base
echo "1. Fake contenttypes..."
python manage.py migrate contenttypes --fake 2>/dev/null || true

echo "2. Fake auth..."
python manage.py migrate auth --fake 2>/dev/null || true

echo "3. Fake sessions..."
python manage.py migrate sessions --fake 2>/dev/null || true

echo "4. Fake admin..."
python manage.py migrate admin --fake 2>/dev/null || true

echo "5. Fake core..."
python manage.py migrate core --fake-initial 2>/dev/null || true

echo "6. Appliquez les migrations manquantes..."
python manage.py migrate 2>/dev/null || true

echo "7. Vérification..."
python manage.py showmigrations

echo "Terminé !"
