"""
Tests de sécurité et permissions (accès non autorisé, rôles)
"""
from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal

from shop.models import User, Category, Product, Cart


class SecurityPermissionsTest(TestCase):
    """Vérifie les restrictions d'accès et les protections basiques"""

    def setUp(self):
        self.client = Client()
        self.customer = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='testpass123',
            role='customer'
        )
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
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            role='admin'
        )
        self.category = Category.objects.create(name='Test')
        self.product_v2 = Product.objects.create(
            vendor=self.vendor2,
            name='Product V2',
            description='Desc',
            price=Decimal('10000.00'),
            category=self.category,
            stock=5
        )

    def test_cart_requires_authentication(self):
        """Un utilisateur non connecté est redirigé depuis /cart"""
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 302)

    def test_customer_cannot_access_vendor_dashboard(self):
        """Un client ne peut pas accéder au dashboard vendeur"""
        self.client.login(username='customer', password='testpass123')
        response = self.client.get(reverse('vendor_dashboard'))
        self.assertIn(response.status_code, [302, 403])

    def test_vendor_cannot_access_admin_dashboard(self):
        """Un vendeur ne peut pas accéder au dashboard admin"""
        self.client.login(username='vendor1', password='testpass123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertIn(response.status_code, [302, 403])

    def test_vendor_cannot_edit_others_product(self):
        """Un vendeur ne peut pas modifier le produit d'un autre vendeur"""
        self.client.login(username='vendor1', password='testpass123')
        url = reverse('vendor_edit_product', args=[self.product_v2.pk])
        data = {
            'name': 'Hack Try',
            'description': 'Hack',
            'price': '20000.00',
            'category': self.category.id,
            'stock': 10
        }
        response = self.client.post(url, data)
        # La vue devrait empêcher/modérer, on accepte 403 ou 302 selon implémentation
        self.assertIn(response.status_code, [302, 403])

        # Le produit ne doit pas être modifié
        self.product_v2.refresh_from_db()
        self.assertEqual(self.product_v2.name, 'Product V2')

    def test_add_to_cart_requires_post(self):
        """Ajouter au panier via GET ne doit pas créer d'item"""
        self.client.login(username='customer', password='testpass123')
        url = reverse('add_to_cart', args=[self.product_v2.pk])
        response_get = self.client.get(url)
        # Généralement 405 (method not allowed), ou redirection; on vérifie juste qu'il n'y a pas de création
        self.assertIn(response_get.status_code, [302, 403, 405, 200])
        self.assertFalse(Cart.objects.filter(user=self.customer, product=self.product_v2).exists())