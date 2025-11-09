"""
Tests d'intégration pour les paiements
"""
from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal

from shop.models import User, Category, Product, Cart, Order


class PaymentIntegrationTest(TestCase):
    """Tests d'intégration du processus de paiement via checkout"""

    def setUp(self):
        self.client = Client()
        # Utilisateur client
        self.customer = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='testpass123',
            role='customer'
        )
        # Vendeur et produit
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
            description='Un super smartphone',
            price=Decimal('50000.00'),
            category=self.category,
            stock=10
        )

    def _prepare_cart(self, quantity=1):
        """Ajouter un produit au panier pour le client"""
        self.client.login(username='customer', password='testpass123')
        url = reverse('add_to_cart', args=[self.product.pk])
        response = self.client.post(url, {'quantity': quantity})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Cart.objects.filter(user=self.customer, product=self.product).exists())

    def _checkout(self, payment_method, reference='REF-TEST-001'):
        """Effectuer le checkout avec une méthode de paiement donnée"""
        data = {
            'shipping_address': '123 Rue Test, Ville',
            'phone': '0123456789',
            'payment_method': payment_method,
            'payment_reference': reference,
        }
        response = self.client.post(reverse('checkout'), data)
        return response

    def test_checkout_orange_money(self):
        """Le checkout avec Orange Money crée une commande avec la bonne méthode"""
        self._prepare_cart(quantity=2)
        response = self._checkout('orange_money', reference='OM-REF-001')
        self.assertEqual(response.status_code, 302)

        order = Order.objects.get(user=self.customer)
        self.assertEqual(order.total_price, Decimal('100000.00'))
        self.assertEqual(order.payment_method, 'orange_money')
        self.assertEqual(order.payment_reference, 'OM-REF-001')

    def test_checkout_mtn_money(self):
        """Le checkout avec MTN Money crée une commande avec la bonne méthode"""
        self._prepare_cart(quantity=1)
        response = self._checkout('mtn_money', reference='MTN-REF-002')
        self.assertEqual(response.status_code, 302)

        order = Order.objects.get(user=self.customer)
        self.assertEqual(order.total_price, Decimal('50000.00'))
        self.assertEqual(order.payment_method, 'mtn_money')
        self.assertEqual(order.payment_reference, 'MTN-REF-002')

    def test_checkout_cash(self):
        """Le checkout en espèces (cash) crée une commande correcte"""
        self._prepare_cart(quantity=3)
        response = self._checkout('cash', reference='CASH-REF-003')
        self.assertEqual(response.status_code, 302)

        order = Order.objects.get(user=self.customer)
        self.assertEqual(order.total_price, Decimal('150000.00'))
        self.assertEqual(order.payment_method, 'cash')
        self.assertEqual(order.payment_reference, 'CASH-REF-003')

    def test_checkout_invalid_method_rejected(self):
        """Une méthode de paiement invalide ne doit pas créer de commande"""
        self._prepare_cart(quantity=1)
        # Poster une méthode invalide — le formulaire doit être invalide et la commande non créée
        response = self._checkout('invalid_method', reference='BAD-REF')
        # Selon l'implémentation, la vue peut renvoyer 200 avec erreurs ou 302
        self.assertIn(response.status_code, [200, 302])
        self.assertFalse(Order.objects.filter(user=self.customer, payment_reference='BAD-REF').exists())