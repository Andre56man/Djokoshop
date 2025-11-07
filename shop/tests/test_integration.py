"""
Tests d'intégration - Scénarios complets
"""
from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from django.core import mail

from shop.models import (
    User, Category, Product, Cart, Order, OrderItem, Notification
)


class CompleteOrderFlowTest(TestCase):
    """Test du flux complet de commande"""
    
    def setUp(self):
        self.client = Client()
        # Créer un client
        self.customer = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='testpass123',
            role='customer'
        )
        # Créer un vendeur
        self.vendor = User.objects.create_user(
            username='vendor',
            email='vendor@example.com',
            password='testpass123',
            role='vendor'
        )
        # Créer une catégorie
        self.category = Category.objects.create(name='Électronique')
        # Créer un produit
        self.product = Product.objects.create(
            vendor=self.vendor,
            name='Smartphone',
            description='Un super smartphone',
            price=Decimal('50000.00'),
            category=self.category,
            stock=10
        )
    
    def test_complete_order_flow(self):
        """Test du flux complet: ajout panier -> checkout -> commande"""
        # 1. Se connecter
        self.client.login(username='customer', password='testpass123')
        
        # 2. Ajouter au panier
        url = reverse('add_to_cart', args=[self.product.pk])
        response = self.client.post(url, {'quantity': 2})
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que le produit est dans le panier
        cart_item = Cart.objects.get(user=self.customer, product=self.product)
        self.assertEqual(cart_item.quantity, 2)
        
        # 3. Aller au checkout
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200)
        
        # 4. Passer la commande
        data = {
            'shipping_address': '123 Rue Test, Ville',
            'phone': '0123456789',
            'payment_method': 'orange_money',
            'payment_reference': 'REF123456'
        }
        response = self.client.post(reverse('checkout'), data)
        self.assertEqual(response.status_code, 302)
        
        # 5. Vérifier que la commande a été créée
        order = Order.objects.get(user=self.customer)
        self.assertEqual(order.total_price, Decimal('100000.00'))  # 2 * 50000
        self.assertEqual(order.status, 'pending')
        
        # 6. Vérifier que les OrderItems ont été créés
        order_items = OrderItem.objects.filter(order=order)
        self.assertEqual(order_items.count(), 1)
        self.assertEqual(order_items.first().quantity, 2)
        
        # 7. Vérifier que le panier a été vidé
        self.assertFalse(Cart.objects.filter(user=self.customer).exists())
        
        # 8. Vérifier qu'une notification a été créée pour le vendeur
        notifications = Notification.objects.filter(user=self.vendor)
        self.assertTrue(notifications.exists())


class VendorProductManagementFlowTest(TestCase):
    """Test du flux de gestion de produits par vendeur"""
    
    def setUp(self):
        self.client = Client()
        self.vendor = User.objects.create_user(
            username='vendor',
            email='vendor@example.com',
            password='testpass123',
            role='vendor'
        )
        self.category = Category.objects.create(name='Électronique')
    
    def test_vendor_product_management_flow(self):
        """Test du flux: ajouter -> modifier -> supprimer produit"""
        # 1. Se connecter en tant que vendeur
        self.client.login(username='vendor', password='testpass123')
        
        # 2. Ajouter un produit
        data = {
            'name': 'New Product',
            'description': 'Product description',
            'price': '25000.00',
            'category': self.category.id,
            'stock': 10
        }
        response = self.client.post(reverse('vendor_add_product'), data)
        self.assertEqual(response.status_code, 302)
        
        product = Product.objects.get(name='New Product')
        self.assertEqual(product.vendor, self.vendor)
        self.assertEqual(product.price, Decimal('25000.00'))
        
        # 3. Modifier le produit
        edit_data = {
            'name': 'Updated Product',
            'description': 'Updated description',
            'price': '30000.00',
            'category': self.category.id,
            'stock': 15
        }
        url = reverse('vendor_edit_product', args=[product.pk])
        response = self.client.post(url, edit_data)
        self.assertEqual(response.status_code, 302)
        
        product.refresh_from_db()
        self.assertEqual(product.name, 'Updated Product')
        self.assertEqual(product.price, Decimal('30000.00'))
        self.assertEqual(product.stock, 15)
        
        # 4. Voir le dashboard vendeur
        response = self.client.get(reverse('vendor_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(product, response.context['products'])
        
        # 5. Supprimer le produit
        url = reverse('vendor_delete_product', args=[product.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Product.objects.filter(pk=product.pk).exists())


class OrderStatusUpdateFlowTest(TestCase):
    """Test du flux de mise à jour du statut de commande"""
    
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
        self.category = Category.objects.create(name='Test')
        self.product = Product.objects.create(
            vendor=self.vendor,
            name='Test Product',
            description='Test',
            price=Decimal('10000.00'),
            category=self.category
        )
        self.order = Order.objects.create(
            user=self.customer,
            total_price=Decimal('20000.00'),
            shipping_address='Test',
            phone='0123456789',
            status='pending'
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=Decimal('10000.00')
        )
    
    def test_vendor_update_order_status(self):
        """Test de mise à jour du statut de commande par le vendeur"""
        # 1. Se connecter en tant que vendeur
        self.client.login(username='vendor', password='testpass123')
        
        # 2. Mettre à jour le statut
        url = reverse('vendor_update_order_status', args=[self.order.id])
        response = self.client.post(url, {'status': 'delivered'})
        self.assertEqual(response.status_code, 302)
        
        # 3. Vérifier que le statut a été mis à jour
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'delivered')
        
        # 4. Vérifier qu'une notification a été créée pour le client
        notifications = Notification.objects.filter(user=self.customer)
        self.assertTrue(notifications.exists())
        self.assertEqual(notifications.first().type, 'order_status')


class SearchAndFilterFlowTest(TestCase):
    """Test du flux de recherche et filtrage"""
    
    def setUp(self):
        self.client = Client()
        self.vendor = User.objects.create_user(
            username='vendor',
            email='vendor@example.com',
            password='testpass123',
            role='vendor'
        )
        self.category1 = Category.objects.create(name='Électronique')
        self.category2 = Category.objects.create(name='Vêtements')
        
        self.product1 = Product.objects.create(
            vendor=self.vendor,
            name='Smartphone Samsung',
            description='Un smartphone',
            price=Decimal('50000.00'),
            category=self.category1
        )
        self.product2 = Product.objects.create(
            vendor=self.vendor,
            name='T-shirt',
            description='Un t-shirt',
            price=Decimal('5000.00'),
            category=self.category2
        )
        self.product3 = Product.objects.create(
            vendor=self.vendor,
            name='Tablette',
            description='Une tablette',
            price=Decimal('30000.00'),
            category=self.category1
        )
    
    def test_search_products(self):
        """Test de recherche de produits"""
        url = reverse('product_list') + '?search=Smartphone'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        products = response.context['products']
        self.assertIn(self.product1, products)
        self.assertNotIn(self.product2, products)
    
    def test_filter_by_category(self):
        """Test de filtrage par catégorie"""
        url = reverse('product_list') + f'?category={self.category1.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        products = response.context['products']
        self.assertIn(self.product1, products)
        self.assertIn(self.product3, products)
        self.assertNotIn(self.product2, products)
    
    def test_search_and_filter_combined(self):
        """Test de recherche et filtrage combinés"""
        url = reverse('product_list') + f'?category={self.category1.id}&search=Tablette'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        products = response.context['products']
        self.assertIn(self.product3, products)
        self.assertNotIn(self.product1, products)
        self.assertNotIn(self.product2, products)

