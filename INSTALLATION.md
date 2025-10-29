# Guide d'Installation - Site E-Commerce Django

## 🚀 Démarrage Rapide

### Étape 1: Installer Python
Assurez-vous d'avoir Python 3.8 ou supérieur installé sur votre système.

### Étape 2: Installer les dépendances
```bash
pip install -r requirements.txt
```

### Étape 3: Créer la base de données
```bash
python manage.py migrate
```

### Étape 4: Créer les catégories par défaut
```bash
python manage.py create_categories
```

### Étape 5: Créer un superutilisateur (Admin)
```bash
python manage.py createsuperuser
```
Répondez aux questions pour créer votre compte administrateur.

### Étape 6: Lancer le serveur
```bash
python manage.py runserver
```

### Étape 7: Accéder au site
- **Site web**: http://127.0.0.1:8000/
- **Panel admin**: http://127.0.0.1:8000/admin/

## 👤 Création de Comptes

### Pour créer un compte Client
1. Allez sur la page d'accueil
2. Cliquez sur "S'inscrire"
3. Remplissez le formulaire
4. Sélectionnez "Client" dans le champ "Je veux être"
5. Cliquez sur "S'inscrire"

### Pour créer un compte Vendeur
1. Allez sur la page d'accueil
2. Cliquez sur "S'inscrire"
3. Remplissez le formulaire
4. Sélectionnez "Vendeur" dans le champ "Je veux être"
5. Cliquez sur "S'inscrire"

### Pour créer un compte Administrateur
Utilisez la commande `createsuperuser` ou créez un compte normal et changez le rôle dans l'admin panel.

## 📦 Utilisation

### En tant que Vendeur
1. Connectez-vous avec votre compte vendeur
2. Accédez au "Tableau de Bord Vendeur"
3. Cliquez sur "Ajouter un produit"
4. Remplissez les informations (nom, description, prix, image, stock, catégorie)
5. Cliquez sur "Ajouter le produit"

### En tant que Client
1. Parcourez les produits
2. Cliquez sur un produit pour voir les détails
3. Ajoutez des produits au panier
4. Allez dans le panier et cliquez sur "Procéder au paiement"
5. Remplissez vos informations et confirmez la commande

### En tant qu'Administrateur
1. Accédez au panel admin (http://127.0.0.1:8000/admin/)
2. Gérez tous les utilisateurs, produits, commandes
3. Accédez au "Tableau de Bord Admin" pour voir les statistiques

## ⚙️ Configuration Email (Optionnel)

Pour activer l'envoi d'emails, modifiez le fichier `ecommerce/settings.py`:

```python
EMAIL_HOST_USER = 'votre-email@gmail.com'
EMAIL_HOST_PASSWORD = 'votre-mot-de-passe-app'
DEFAULT_FROM_EMAIL = 'votre-email@gmail.com'
```

**Note**: Pour Gmail, créez un "mot de passe d'application" dans vos paramètres de compte Google.

## 🎨 Personnalisation

### Modifier les couleurs
Éditez le fichier `static/css/style.css` et modifiez les variables CSS dans `:root`:

```css
:root {
    --primary-color: #000000;
    --accent-color: #c9a961;
    /* etc. */
}
```

### Ajouter des catégories
```bash
python manage.py shell
```

Puis dans le shell Python:
```python
from shop.models import Category
Category.objects.create(name="Ma Catégorie", slug="ma-categorie")
```

## 🐛 Problèmes Courants

### Erreur: No module named 'Pillow'
```bash
pip install -r requirements.txt
```

### Erreur: Table doesn't exist
```bash
python manage.py migrate
```

### Images ne s'affichent pas
Vérifiez que le dossier `media/` existe et que les permissions sont correctes.

## 📝 Notes

- La devise utilisée est le Franc CFA (FCFA)
- Les images sont stockées dans le dossier `media/products/`
- La base de données SQLite est dans `db.sqlite3`
- En production, utilisez PostgreSQL ou MySQL au lieu de SQLite

## 🔒 Sécurité (Pour Production)

1. Changez le SECRET_KEY dans `settings.py`
2. Activez DEBUG = False
3. Configurez les ALLOWED_HOSTS
4. Utilisez HTTPS
5. Changez de SQLite vers PostgreSQL ou MySQL
6. Configurez correctement les fichiers statiques

## 🆘 Support

Pour toute question ou problème, contactez: contact@maboutique.com

