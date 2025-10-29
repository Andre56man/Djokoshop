# Site E-Commerce Django

Un site e-commerce moderne développé avec Django, inspiré du design de Zara et Nike.

## Fonctionnalités

### Pour les Clients
- Inscription et authentification
- Parcourir les produits par catégorie
- Rechercher des produits
- Ajouter des produits au panier
- Passer une commande
- Voir l'historique des commandes

### Pour les Vendeurs
- Inscription en tant que vendeur
- Ajouter, modifier et supprimer des produits
- Gérer le stock
- Voir les statistiques de ventes
- Tableau de bord dédié

### Pour les Administrateurs
- Gestion complète de la plateforme
- Voir toutes les statistiques
- Surveiller les commandes
- Panel d'administration Django

## Installation

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Cloner le projet** (ou naviguer dans le dossier)
```bash
cd Testval
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
```

3. **Activer l'environnement virtuel**
- Sur Windows:
```bash
venv\Scripts\activate
```
- Sur Mac/Linux:
```bash
source venv/bin/activate
```

4. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

5. **Configurer la base de données**
```bash
python manage.py migrate
```

6. **Créer un superutilisateur (admin)**
```bash
python manage.py createsuperuser
```

7. **Collecter les fichiers statiques**
```bash
python manage.py collectstatic --noinput
```

8. **Lancer le serveur de développement**
```bash
python manage.py runserver
```

9. **Accéder au site**
- Site web: http://127.0.0.1:8000/
- Admin panel: http://127.0.0.1:8000/admin/

## Configuration Email (SMTP)

Pour activer l'envoi d'emails, modifiez le fichier `ecommerce/settings.py`:

```python
EMAIL_HOST_USER = 'your-email@gmail.com'  # Votre email
EMAIL_HOST_PASSWORD = 'your-app-password'  # Mot de passe d'application
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
```

Note: Pour Gmail, vous devez créer un "mot de passe d'application" dans les paramètres de votre compte Google.

## Structure du Projet

```
Testval/
├── manage.py
├── requirements.txt
├── README.md
├── ecommerce/          # Configuration du projet
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── ...
├── shop/               # Application principale
│   ├── models.py      # Modèles de données
│   ├── views.py       # Vues
│   ├── forms.py       # Formulaires
│   ├── admin.py       # Interface admin
│   ├── urls.py        # URLs
│   ├── templates/     # Templates HTML
│   └── ...
├── static/            # Fichiers statiques (CSS, JS, images)
│   └── css/
│       └── style.css
├── media/             # Fichiers uploadés (images produits)
└── db.sqlite3         # Base de données SQLite
```

## Utilisation

### Créer des catégories de produits
Accédez au panel d'administration Django et créez des catégories.

### Créer des comptes
- **Client**: Inscrivez-vous comme "Client"
- **Vendeur**: Inscrivez-vous comme "Vendeur"
- **Admin**: Créez un superutilisateur avec la commande `createsuperuser`

### Gérer les produits
Les vendeurs peuvent ajouter, modifier et supprimer leurs produits depuis leur tableau de bord.

### Passer une commande
1. Ajoutez des produits au panier
2. Allez dans le panier
3. Cliquez sur "Procéder au paiement"
4. Remplissez vos informations de livraison
5. Confirmez la commande

## Devise
Le site utilise le Franc CFA (FCFA) comme devise monétaire.

## Design
Le design est inspiré des sites web modernes de Zara et Nike, avec:
- Interface minimaliste et élégante
- Palette de couleurs noir et blanc
- Typographie moderne
- Expérience utilisateur optimale

## Développement
Développé par un développeur avec 15 ans d'expérience en développement web.

## Support
Pour toute question, contactez: contact@maboutique.com

## Licence
Tous droits réservés © 2024

