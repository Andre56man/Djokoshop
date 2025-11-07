"""
Tests pour les permissions et rôles
"""
from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal

from shop.models import User, Category, Product, Order
from shop.views import is_vendor, is_admin


class RolePermissionTest(TestCase):
    """Tests pour les permissions basées sur les rôles"""
    
    def setUp(self):
        self.client = Client()
        self.customer = User.objects.create_user(
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
    
    def test_is_vendor_function(self):
        """Test de la fonction is_vendor"""
        self.assertFalse(is_vendor(self.customer))
        self.assertTrue(is_vendor(self.vendor))
        self.assertFalse(is_vendor(self.admin))
        self.assertFalse(is_vendor(self.superuser))
    
    def test_is_admin_function(self):
        """Test de la fonction is_admin"""
        self.assertFalse(is_admin(self.customer))
        self.assertFalse(is_admin(self.vendor))
        self.assertTrue(is_admin(self.admin))
        self.assertTrue(is_admin(self.superuser))
    
    def test_vendor_dashboard_customer_access(self):
        """Test qu'un client ne peut pas accéder au dashboard vendeur"""
        self.client.login(username='customer', password='testpass123')
        response = self.client.get(reverse('vendor_dashboard'))
        # user_passes_test peut rediriger ou retourner 403 selon la configuration
        self.assertIn(response.status_code, [302, 403])
    
    def test_vendor_dashboard_vendor_access(self):
        """Test qu'un vendeur peut accéder au dashboard vendeur"""
        self.client.login(username='vendor', password='testpass123')
        response = self.client.get(reverse('vendor_dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_vendor_add_product_customer_access(self):
        """Test qu'un client ne peut pas ajouter de produit"""
        self.client.login(username='customer', password='testpass123')
        response = self.client.get(reverse('vendor_add_product'))
        # user_passes_test peut rediriger ou retourner 403 selon la configuration
        self.assertIn(response.status_code, [302, 403])
    
    def test_vendor_add_product_vendor_access(self):
        """Test qu'un vendeur peut ajouter un produit"""
        self.client.login(username='vendor', password='testpass123')
        response = self.client.get(reverse('vendor_add_product'))
        self.assertEqual(response.status_code, 200)
    
    def test_admin_dashboard_customer_access(self):
        """Test qu'un client ne peut pas accéder au dashboard admin"""
        self.client.login(username='customer', password='testpass123')
        response = self.client.get(reverse('admin_dashboard'))
        # user_passes_test peut rediriger ou retourner 403 selon la configuration
        self.assertIn(response.status_code, [302, 403])
    
    def test_admin_dashboard_vendor_access(self):
        """Test qu'un vendeur ne peut pas accéder au dashboard admin"""
        self.client.login(username='vendor', password='testpass123')
        response = self.client.get(reverse('admin_dashboard'))
        # user_passes_test peut rediriger ou retourner 403 selon la configuration
        self.assertIn(response.status_code, [302, 403])
    
    def test_admin_dashboard_admin_access(self):
        """Test qu'un admin peut accéder au dashboard admin"""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_admin_dashboard_superuser_access(self):
        """Test qu'un superuser peut accéder au dashboard admin"""
        self.client.login(username='superuser', password='testpass123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)


class ProductOwnershipTest(TestCase):
    """Tests pour la propriété des produits"""
    
    def setUp(self):
        self.client = Client()
        self.vendor1 = User.objects.create_user(
            username='vendor1',
            email='vendor1@example.com',
            password='testpass123',
            role='vendor'
        )
        self.vendor2 = User.objects.create_user(
            username='vendor2',
            email='vendor2@example.com',
            password='testpass123',
            role='vendor'
        )
        self.category = Category.objects.create(name='Test')
        self.product1 = Product.objects.create(
            vendor=self.vendor1,
            name='Product 1',
            description='Test',
            price=Decimal('10000.00'),
            category=self.category
        )
        self.product2 = Product.objects.create(
            vendor=self.vendor2,
            name='Product 2',
            description='Test',
            price=Decimal('20000.00'),
            category=self.category
        )
    
    def test_vendor_can_edit_own_product(self):
        """Test qu'un vendeur peut modifier son propre produit"""
        self.client.login(username='vendor1', password='testpass123')
        url = reverse('vendor_edit_product', args=[self.product1.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_vendor_cannot_edit_other_vendor_product(self):
        """Test qu'un vendeur ne peut pas modifier le produit d'un autre vendeur"""
        self.client.login(username='vendor1', password='testpass123')
        url = reverse('vendor_edit_product', args=[self.product2.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)  # get_object_or_404 retourne 404
    
    def test_vendor_can_delete_own_product(self):
        """Test qu'un vendeur peut supprimer son propre produit"""
        self.client.login(username='vendor1', password='testpass123')
        url = reverse('vendor_delete_product', args=[self.product1.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Product.objects.filter(pk=self.product1.pk).exists())
    
    def test_vendor_cannot_delete_other_vendor_product(self):
        """Test qu'un vendeur ne peut pas supprimer le produit d'un autre vendeur"""
        self.client.login(username='vendor1', password='testpass123')
        url = reverse('vendor_delete_product', args=[self.product2.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        # Vérifier que le produit existe toujours
        self.assertTrue(Product.objects.filter(pk=self.product2.pk).exists())


class OrderAccessTest(TestCase):
    """Tests pour l'accès aux commandes"""
    
    def setUp(self):
        self.client = Client()
        self.customer1 = User.objects.create_user(
            username='customer1',
            email='customer1@example.com',
            password='testpass123',
            role='customer'
        )
        self.customer2 = User.objects.create_user(
            username='customer2',
            email='customer2@example.com',
            password='testpass123',
            role='customer'
        )
        self.order1 = Order.objects.create(
            user=self.customer1,
            total_price=Decimal('10000.00'),
            shipping_address='Address 1',
            phone='0123456789'
        )
        self.order2 = Order.objects.create(
            user=self.customer2,
            total_price=Decimal('20000.00'),
            shipping_address='Address 2',
            phone='0987654321'
        )
    
    def test_customer_can_view_own_order(self):
        """Test qu'un client peut voir sa propre commande"""
        self.client.login(username='customer1', password='testpass123')
        url = reverse('order_detail', args=[self.order1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['order'], self.order1)
    
    def test_customer_cannot_view_other_customer_order(self):
        """Test qu'un client ne peut pas voir la commande d'un autre client"""
        self.client.login(username='customer1', password='testpass123')
        url = reverse('order_detail', args=[self.order2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)  # get_object_or_404 retourne 404
    
    def test_my_orders_shows_only_own_orders(self):
        """Test que 'mes commandes' affiche uniquement les commandes de l'utilisateur"""
        self.client.login(username='customer1', password='testpass123')
        response = self.client.get(reverse('my_orders'))
        self.assertEqual(response.status_code, 200)
        orders = response.context['orders']
        self.assertIn(self.order1, orders)
        self.assertNotIn(self.order2, orders)

