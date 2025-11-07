# Tests Fonctionnels - Djokoshop

Ce dossier contient tous les tests fonctionnels pour l'application shop.

## Structure des Tests

- `test_models.py` - Tests pour les modèles (User, Product, Order, Cart, etc.)
- `test_views.py` - Tests pour les vues (pages, redirections, templates)
- `test_forms.py` - Tests pour les formulaires (validation, sauvegarde)
- `test_auth.py` - Tests d'authentification (login, vérification email, reset password)
- `test_permissions.py` - Tests des permissions et rôles (customer, vendor, admin)
- `test_context_processors.py` - Tests pour les context processors
- `test_integration.py` - Tests d'intégration (flux complets)

## Exécution des Tests

### Exécuter tous les tests

```bash
python manage.py test shop.tests
```

### Exécuter un fichier de test spécifique

```bash
# Tests des modèles
python manage.py test shop.tests.test_models

# Tests des vues
python manage.py test shop.tests.test_views

# Tests d'authentification
python manage.py test shop.tests.test_auth

# Tests de permissions
python manage.py test shop.tests.test_permissions

# Tests d'intégration
python manage.py test shop.tests.test_integration
```

### Exécuter une classe de test spécifique

```bash
python manage.py test shop.tests.test_models.UserModelTest
```

### Exécuter un test spécifique

```bash
python manage.py test shop.tests.test_models.UserModelTest.test_user_creation
```

### Exécuter avec verbosité

```bash
python manage.py test shop.tests --verbosity=2
```

## Couverture des Tests

### Modèles Testés
- ✅ User (création, rôles, vérification)
- ✅ Category (création, slug automatique)
- ✅ Product (création, prix formaté)
- ✅ Cart (ajout, calcul total)
- ✅ Order (création, statuts)
- ✅ OrderItem (création, calcul)
- ✅ PasswordResetToken (expiration)
- ✅ Notification (création, lecture)
- ✅ Tag (création)

### Vues Testées
- ✅ Home (page d'accueil)
- ✅ ProductList (liste, recherche, filtrage)
- ✅ ProductDetail (détails produit)
- ✅ Register (inscription)
- ✅ Login (connexion)
- ✅ Cart (affichage, ajout, suppression)
- ✅ Checkout (passage de commande)
- ✅ MyOrders (liste des commandes)
- ✅ OrderDetail (détails de commande)
- ✅ VendorDashboard (dashboard vendeur)
- ✅ VendorAddProduct (ajout produit)
- ✅ VendorEditProduct (modification produit)
- ✅ VendorDeleteProduct (suppression produit)
- ✅ AdminDashboard (dashboard admin)
- ✅ NotificationsList (liste notifications)
- ✅ Profile (profil utilisateur)

### Formulaires Testés
- ✅ CustomUserCreationForm (inscription)
- ✅ ProductForm (création/modification produit)
- ✅ CheckoutForm (checkout)
- ✅ UserPreferencesForm (préférences utilisateur)
- ✅ AdminUserEditForm (édition admin)

### Permissions Testées
- ✅ Accès vendeur (vendor_dashboard, add_product, etc.)
- ✅ Accès admin (admin_dashboard)
- ✅ Propriété des produits (un vendeur ne peut modifier que ses produits)
- ✅ Accès aux commandes (un client ne voit que ses commandes)

### Flux d'Intégration Testés
- ✅ Flux complet de commande (panier -> checkout -> commande)
- ✅ Flux de gestion de produits (ajout -> modification -> suppression)
- ✅ Flux de mise à jour de statut de commande
- ✅ Flux de recherche et filtrage

## Notes Importantes

1. **Base de données de test** : Django crée automatiquement une base de données de test temporaire pour chaque exécution de tests.

2. **Données de test** : Chaque test crée ses propres données via `setUp()`. Les données sont nettoyées après chaque test.

3. **Authentification** : Utilisez `self.client.login()` pour tester les vues nécessitant une authentification.

4. **Emails** : Les emails envoyés sont stockés dans `django.core.mail.outbox` pendant les tests.

5. **Fixtures** : Si nécessaire, vous pouvez créer des fixtures JSON pour des données de test complexes.

## Améliorations Futures

- [ ] Tests de performance
- [ ] Tests de sécurité (CSRF, XSS, etc.)
- [ ] Tests d'API (si API REST ajoutée)
- [ ] Tests avec Selenium (tests end-to-end)
- [ ] Couverture de code avec coverage.py

## Exemple de Test

```python
def test_product_creation(self):
    """Test de création d'un produit"""
    product = Product.objects.create(
        vendor=self.vendor,
        name='Test Product',
        description='Test',
        price=Decimal('10000.00'),
        category=self.category
    )
    self.assertEqual(product.name, 'Test Product')
    self.assertEqual(product.price, Decimal('10000.00'))
```

## Résolution de Problèmes

### Erreur: "No such table"
```bash
python manage.py migrate
python manage.py test
```

### Erreur: "Module not found"
Vérifiez que vous êtes dans le bon répertoire et que l'environnement virtuel est activé.

### Tests qui échouent
Utilisez `--verbosity=2` pour voir plus de détails sur les erreurs.

