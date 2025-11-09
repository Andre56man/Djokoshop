"""
Tests de cas limites pour le panier: doublons, suppression, agrégation de quantités
"""
from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal

from shop.models import User, Category, Product, Cart


class CartEdgeCasesTest(TestCase):
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
        self.category = Category.objects.create(name='Divers')
        self.product = Product.objects.create(
            vendor=self.vendor,
            name='Casque Audio',
            description='Casque',
            price=Decimal('25000.00'),
            category=self.category,
            stock=8
        )
        self.client.login(username='customer', password='testpass123')

    def test_add_same_product_twice_aggregates_quantity(self):
        """Ajouter le même produit deux fois agrège la quantité au lieu de créer des doublons"""
        url = reverse('add_to_cart', args=[self.product.pk])
        r1 = self.client.post(url, {'quantity': 2})
        r2 = self.client.post(url, {'quantity': 3})
        self.assertEqual(r1.status_code, 302)
        self.assertEqual(r2.status_code, 302)

        item = Cart.objects.get(user=self.customer, product=self.product)
        self.assertEqual(item.quantity, 5)

    def test_remove_item_from_cart(self):
        """Supprimer un article du panier via la vue dédiée"""
        add_url = reverse('add_to_cart', args=[self.product.pk])
        self.client.post(add_url, {'quantity': 1})
        self.assertTrue(Cart.objects.filter(user=self.customer, product=self.product).exists())

        remove_url = reverse('remove_from_cart', args=[self.product.pk])
        response = self.client.post(remove_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Cart.objects.filter(user=self.customer, product=self.product).exists())