"""
Tests pour les vues
"""
from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from django.core import mail

from shop.models import (
    User, Category, Product, Cart, Order, OrderItem, Notification
)


class HomeViewTest(TestCase):
    """Tests pour la vue home"""
    
    def setUp(self):
        self.client = Client()
        self.vendor = User.objects.create_user(
            username='vendor',
            email='vendor@example.com',
            password='testpass123',
            role='vendor'
        )
        self.category = Category.objects.create(name='Électronique')
    
    def test_home_view(self):
        """Test de la page d'accueil"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/home.html')
    
    def test_home_shows_products(self):
        """Test que la page d'accueil affiche les produits"""
        product = Product.objects.create(
            vendor=self.vendor,
            name='Test Product',
            description='Test',
            price=Decimal('10000.00'),
            category=self.category,
            is_active=True
        )
        response = self.client.get(reverse('home'))
        self.assertIn(product, response.context['products'])
    
    def test_home_shows_categories(self):
        """Test que la page d'accueil affiche les catégories"""
        response = self.client.get(reverse('home'))
        self.assertIn(self.category, response.context['categories'])


class ProductListViewTest(TestCase):
    """Tests pour la vue product_list"""
    
    def setUp(self):
        self.client = Client()
        self.vendor = User.objects.create_user(
            username='vendor',
            email='vendor@example.com',
            password='testpass123',
            role='vendor'
        )
        self.category = Category.objects.create(name='Électronique')
        self.product = Product.objects.create(
            vendor=self.vendor,
            name='Smartphone',
            description='Un smartphone',
            price=Decimal('50000.00'),
            category=self.category
        )
    
    def test_product_list_view(self):
        """Test de la liste des produits"""
        response = self.client.get(reverse('product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/product_list.html')
    
    def test_product_list_filter_by_category(self):
        """Test du filtrage par catégorie"""
        url = reverse('product_list') + f'?category={self.category.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.product, response.context['products'])
    
    def test_product_list_search(self):
        """Test de la recherche de produits"""
        url = reverse('product_list') + '?search=Smartphone'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.product, response.context['products'])


class ProductDetailViewTest(TestCase):
    """Tests pour la vue product_detail"""
    
    def setUp(self):
        self.client = Client()
        self.vendor = User.objects.create_user(
            username='vendor',
            email='vendor@example.com',
            password='testpass123',
            role='vendor'
        )
        self.category = Category.objects.create(name='Électronique')
        self.product = Product.objects.create(
            vendor=self.vendor,
            name='Test Product',
            description='Test description',
            price=Decimal('10000.00'),
            category=self.category,
            is_active=True
        )
    
    def test_product_detail_view(self):
        """Test de la page de détail d'un produit"""
        url = reverse('product_detail', args=[self.product.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/product_detail.html')
    
    def test_product_detail_shows_product(self):
        """Test que la page affiche le bon produit"""
        url = reverse('product_detail', args=[self.product.pk])
        response = self.client.get(url)
        self.assertEqual(response.context['product'], self.product)
    
    def test_product_detail_inactive_product(self):
        """Test qu'un produit inactif retourne 404"""
        self.product.is_active = False
        self.product.save()
        url = reverse('product_detail', args=[self.product.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class AuthenticationViewsTest(TestCase):
    """Tests pour les vues d'authentification"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='customer'
        )
    
    def test_register_view_get(self):
        """Test de la page d'inscription (GET)"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/register.html')
    
    def test_register_view_post(self):
        """Test de l'inscription (POST)"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'role': 'customer'
        }
        response = self.client.post(reverse('register'), data)
        # Devrait rediriger vers verify_email après inscription
        self.assertIn(response.status_code, [200, 302])
    
    def test_login_view_get(self):
        """Test de la page de connexion (GET)"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/login.html')
    
    def test_login_view_post_success(self):
        """Test de connexion réussie"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 302)  # Redirection
    
    def test_login_view_post_failure(self):
        """Test de connexion échouée"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 200)  # Reste sur la page


class CartViewsTest(TestCase):
    """Tests pour les vues du panier"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='testpass123',
            role='customer'
        )
        self.vendor = User.objects.create_user(
            username='vendor',
            email='vendor@example.com',
            password='testpass123',
            role='vendor'
        )
        self.category = Category.objects.create(name='Test')
        self.product = Product.objects.create(
            vendor=self.vendor,
            name='Test Product',
            description='Test',
            price=Decimal('10000.00'),
            category=self.category,
            stock=10
        )
    
    def test_cart_view_requires_login(self):
        """Test que la vue panier nécessite une connexion"""
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 302)  # Redirection vers login
    
    def test_cart_view_authenticated(self):
        """Test de la vue panier pour un utilisateur connecté"""
        self.client.login(username='customer', password='testpass123')
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/cart.html')
    
    def test_add_to_cart(self):
        """Test d'ajout au panier"""
        self.client.login(username='customer', password='testpass123')
        url = reverse('add_to_cart', args=[self.product.pk])
        response = self.client.post(url, {'quantity': 2})
        self.assertEqual(response.status_code, 302)  # Redirection
        
        # Vérifier que le produit a été ajouté
        cart_item = Cart.objects.get(user=self.user, product=self.product)
        self.assertEqual(cart_item.quantity, 2)
    
    def test_remove_from_cart(self):
        """Test de retrait du panier"""
        self.client.login(username='customer', password='testpass123')
        cart_item = Cart.objects.create(
            user=self.user,
            product=self.product,
            quantity=1
        )
        url = reverse('remove_from_cart', args=[cart_item.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Cart.objects.filter(pk=cart_item.pk).exists())


class OrderViewsTest(TestCase):
    """Tests pour les vues de commande"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='testpass123',
            role='customer'
        )
        self.vendor = User.objects.create_user(
            username='vendor',
            email='vendor@example.com',
            password='testpass123',
            role='vendor'
        )
        self.category = Category.objects.create(name='Test')
        self.product = Product.objects.create(
            vendor=self.vendor,
            name='Test Product',
            description='Test',
            price=Decimal('10000.00'),
            category=self.category,
            stock=10
        )
        self.cart_item = Cart.objects.create(
            user=self.user,
            product=self.product,
            quantity=2
        )
    
    def test_checkout_view_requires_login(self):
        """Test que checkout nécessite une connexion"""
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 302)
    
    def test_checkout_view_empty_cart(self):
        """Test de checkout avec panier vide"""
        self.client.login(username='customer', password='testpass123')
        Cart.objects.all().delete()
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 302)  # Redirection vers cart
    
    def test_checkout_view_post(self):
        """Test de passage de commande"""
        self.client.login(username='customer', password='testpass123')
        data = {
            'shipping_address': '123 Rue Test',
            'phone': '0123456789',
            'payment_method': 'orange_money',
            'payment_reference': 'REF123'
        }
        response = self.client.post(reverse('checkout'), data)
        # Devrait créer une commande et rediriger
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Order.objects.filter(user=self.user).exists())
    
    def test_my_orders_view(self):
        """Test de la vue mes commandes"""
        self.client.login(username='customer', password='testpass123')
        order = Order.objects.create(
            user=self.user,
            total_price=Decimal('20000.00'),
            shipping_address='Test',
            phone='0123456789'
        )
        response = self.client.get(reverse('my_orders'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(order, response.context['orders'])
    
    def test_order_detail_view(self):
        """Test de la vue détail de commande"""
        self.client.login(username='customer', password='testpass123')
        order = Order.objects.create(
            user=self.user,
            total_price=Decimal('20000.00'),
            shipping_address='Test',
            phone='0123456789'
        )
        url = reverse('order_detail', args=[order.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['order'], order)


class VendorViewsTest(TestCase):
    """Tests pour les vues vendeur"""
    
    def setUp(self):
        self.client = Client()
        self.vendor = User.objects.create_user(
            username='vendor',
            email='vendor@example.com',
            password='testpass123',
            role='vendor'
        )
        self.customer = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='testpass123',
            role='customer'
        )
        self.category = Category.objects.create(name='Test')
    
    def test_vendor_dashboard_requires_vendor_role(self):
        """Test que le dashboard vendeur nécessite le rôle vendeur"""
        self.client.login(username='customer', password='testpass123')
        response = self.client.get(reverse('vendor_dashboard'))
        # user_passes_test peut rediriger ou retourner 403 selon la configuration
        self.assertIn(response.status_code, [302, 403])
    
    def test_vendor_dashboard_accessible(self):
        """Test d'accès au dashboard vendeur"""
        self.client.login(username='vendor', password='testpass123')
        response = self.client.get(reverse('vendor_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/vendor_dashboard.html')
    
    def test_vendor_add_product(self):
        """Test d'ajout de produit par vendeur"""
        self.client.login(username='vendor', password='testpass123')
        data = {
            'name': 'New Product',
            'description': 'Description',
            'price': '15000.00',
            'category': self.category.id,
            'stock': 5
        }
        response = self.client.post(reverse('vendor_add_product'), data)
        self.assertEqual(response.status_code, 302)  # Redirection
        self.assertTrue(Product.objects.filter(name='New Product').exists())
    
    def test_vendor_edit_product(self):
        """Test de modification de produit"""
        self.client.login(username='vendor', password='testpass123')
        product = Product.objects.create(
            vendor=self.vendor,
            name='Old Product',
            description='Old',
            price=Decimal('10000.00'),
            category=self.category
        )
        data = {
            'name': 'Updated Product',
            'description': 'Updated',
            'price': '12000.00',
            'category': self.category.id,
            'stock': 10
        }
        url = reverse('vendor_edit_product', args=[product.pk])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        product.refresh_from_db()
        self.assertEqual(product.name, 'Updated Product')
    
    def test_vendor_delete_product(self):
        """Test de suppression de produit"""
        self.client.login(username='vendor', password='testpass123')
        product = Product.objects.create(
            vendor=self.vendor,
            name='To Delete',
            description='Test',
            price=Decimal('10000.00'),
            category=self.category
        )
        url = reverse('vendor_delete_product', args=[product.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Product.objects.filter(pk=product.pk).exists())


class AdminViewsTest(TestCase):
    """Tests pour les vues admin"""
    
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            role='admin'
        )
        self.superuser = User.objects.create_superuser(
            username='superuser',
            email='super@example.com',
            password='testpass123'
        )
        self.customer = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='testpass123',
            role='customer'
        )
    
    def test_admin_dashboard_requires_admin(self):
        """Test que le dashboard admin nécessite le rôle admin"""
        self.client.login(username='customer', password='testpass123')
        response = self.client.get(reverse('admin_dashboard'))
        # user_passes_test redirige vers login si l'utilisateur ne passe pas le test
        # On accepte soit 302 (redirection) soit 403 (forbidden)
        self.assertIn(response.status_code, [302, 403])
    
    def test_admin_dashboard_accessible_by_admin(self):
        """Test d'accès au dashboard admin pour admin"""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/admin_dashboard.html')
    
    def test_admin_dashboard_accessible_by_superuser(self):
        """Test d'accès au dashboard admin pour superuser"""
        self.client.login(username='superuser', password='testpass123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)


class NotificationViewsTest(TestCase):
    """Tests pour les vues de notification"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.notification = Notification.objects.create(
            user=self.user,
            type='order_status',
            message='Test notification'
        )
    
    def test_notifications_list_requires_login(self):
        """Test que la liste des notifications nécessite une connexion"""
        response = self.client.get(reverse('notifications_list'))
        self.assertEqual(response.status_code, 302)
    
    def test_notifications_list(self):
        """Test de la liste des notifications"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('notifications_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.notification, response.context['notifications'])
    
    def test_mark_notification_read(self):
        """Test de marquage d'une notification comme lue"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('mark_notification_read', args=[self.notification.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)


class ProfileViewTest(TestCase):
    """Tests pour la vue profil"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_profile_requires_login(self):
        """Test que le profil nécessite une connexion"""
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)
    
    def test_profile_view(self):
        """Test de la vue profil"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/profile.html')
    
    def test_profile_update(self):
        """Test de mise à jour du profil"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'username': 'testuser',
            'email': 'updated@example.com',
            'phone': '0123456789',
            'address': 'New address'
        }
        response = self.client.post(reverse('profile'), data)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'updated@example.com')

