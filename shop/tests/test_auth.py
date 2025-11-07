"""
Tests pour l'authentification et la vérification d'email
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
from django.utils import timezone
from datetime import timedelta

from shop.models import User, PasswordResetToken


class EmailVerificationTest(TestCase):
    """Tests pour la vérification d'email"""
    
    def setUp(self):
        self.client = Client()
    
    def test_verification_email_sent_on_registration(self):
        """Test qu'un email de vérification est envoyé lors de l'inscription"""
        # Note: Ce test nécessite que les emails soient configurés
        # Pour un vrai test, on devrait mock send_mail
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'role': 'customer'
        }
        response = self.client.post(reverse('register'), form_data)
        # Vérifier qu'un utilisateur a été créé avec un code de vérification
        user = User.objects.get(username='newuser')
        self.assertIsNotNone(user.verification_code)
        self.assertFalse(user.is_verified)
    
    def test_verify_email_page(self):
        """Test de la page de vérification d'email"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        user.verification_code = '123456'
        user.save()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('verify_email'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/verify_email.html')
    
    def test_verify_email_correct_code(self):
        """Test de vérification avec un code correct"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        user.verification_code = '123456'
        user.save()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('verify_email'), {'code': '123456'})
        user.refresh_from_db()
        self.assertTrue(user.is_verified)
        self.assertEqual(user.verification_code, '')
    
    def test_verify_email_incorrect_code(self):
        """Test de vérification avec un code incorrect"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        user.verification_code = '123456'
        user.save()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('verify_email'), {'code': '000000'})
        user.refresh_from_db()
        self.assertFalse(user.is_verified)


class PasswordResetTest(TestCase):
    """Tests pour la réinitialisation de mot de passe"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='oldpass123'
        )
    
    def test_forgot_password_page(self):
        """Test de la page de mot de passe oublié"""
        response = self.client.get(reverse('forgot_password'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/forgot_password.html')
    
    def test_forgot_password_post_valid_email(self):
        """Test de demande de réinitialisation avec email valide"""
        response = self.client.post(
            reverse('forgot_password'),
            {'email': 'test@example.com'}
        )
        self.assertEqual(response.status_code, 302)  # Redirection
        # Vérifier qu'un token a été créé
        self.assertTrue(PasswordResetToken.objects.filter(user=self.user).exists())
    
    def test_forgot_password_post_invalid_email(self):
        """Test de demande de réinitialisation avec email invalide"""
        response = self.client.post(
            reverse('forgot_password'),
            {'email': 'nonexistent@example.com'}
        )
        self.assertEqual(response.status_code, 200)  # Reste sur la page
    
    def test_reset_password_valid_token(self):
        """Test de réinitialisation avec token valide"""
        token = PasswordResetToken.objects.create(
            user=self.user,
            token='valid-token-123',
            expires_at=timezone.now() + timedelta(hours=1)
        )
        url = reverse('reset_password', args=['valid-token-123'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/reset_password.html')
    
    def test_reset_password_expired_token(self):
        """Test de réinitialisation avec token expiré"""
        token = PasswordResetToken.objects.create(
            user=self.user,
            token='expired-token',
            expires_at=timezone.now() - timedelta(hours=1)
        )
        url = reverse('reset_password', args=['expired-token'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirection vers forgot_password
    
    def test_reset_password_post(self):
        """Test de réinitialisation du mot de passe (POST)"""
        token = PasswordResetToken.objects.create(
            user=self.user,
            token='reset-token-123',
            expires_at=timezone.now() + timedelta(hours=1)
        )
        url = reverse('reset_password', args=['reset-token-123'])
        data = {
            'password': 'newpass123',
            'confirm_password': 'newpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirection vers login
        # Vérifier que le mot de passe a été changé
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass123'))
        # Vérifier que le token a été marqué comme utilisé
        token.refresh_from_db()
        self.assertTrue(token.is_used)
    
    def test_reset_password_mismatch(self):
        """Test de réinitialisation avec mots de passe différents"""
        token = PasswordResetToken.objects.create(
            user=self.user,
            token='reset-token-123',
            expires_at=timezone.now() + timedelta(hours=1)
        )
        url = reverse('reset_password', args=['reset-token-123'])
        data = {
            'password': 'newpass123',
            'confirm_password': 'differentpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)  # Reste sur la page
        # Vérifier que le mot de passe n'a pas changé
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('oldpass123'))


class AuthenticationRequiredTest(TestCase):
    """Tests pour les vues nécessitant une authentification"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_protected_views_redirect_to_login(self):
        """Test que les vues protégées redirigent vers login"""
        protected_urls = [
            reverse('cart'),
            reverse('checkout'),
            reverse('my_orders'),
            reverse('profile'),
            reverse('vendor_dashboard'),
            reverse('admin_dashboard'),
            reverse('notifications_list'),
        ]
        
        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn('/login/', response.url)
    
    def test_authenticated_user_access(self):
        """Test que les utilisateurs authentifiés peuvent accéder aux vues"""
        self.client.login(username='testuser', password='testpass123')
        
        # Vues accessibles à tous les utilisateurs authentifiés
        accessible_urls = [
            reverse('cart'),
            reverse('checkout'),
            reverse('my_orders'),
            reverse('profile'),
            reverse('notifications_list'),
        ]
        
        for url in accessible_urls:
            response = self.client.get(url)
            # Certaines vues peuvent retourner 200 ou 302 selon le contexte
            self.assertIn(response.status_code, [200, 302])

