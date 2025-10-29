# Configuration Gmail pour les Emails - GUIDE COMPLET

## ⚠️ Problème Principal: Vous ne recevez pas les emails

Si vous configurez Gmail mais que vous ne recevez pas les emails, c'est probablement à cause de la sécurité de Google.

## ✅ Solution: Utiliser un "Mot de passe d'application"

Gmail ne permet PLUS d'utiliser votre mot de passe normal pour les applications tierces. Vous DEVEZ créer un "mot de passe d'application".

### Étapes pour créer un mot de passe d'application Google:

#### 1. Activer la vérification en 2 étapes
   - Allez sur https://myaccount.google.com/security
   - Cliquez sur "Vérification en 2 étapes"
   - Suivez les instructions pour l'activer (c'est OBLIGATOIRE)

#### 2. Créer un mot de passe d'application
   - Allez sur https://myaccount.google.com/apppasswords
   - Sélectionnez "Mail" comme application
   - Sélectionnez "Autre" comme appareil et tapez "Django E-commerce"
   - Cliquez sur "Générer"
   - **Google va vous donner un code de 16 caractères** (par exemple: `abcd efgh ijkl mnop`)

#### 3. Utiliser ce code dans votre projet
   Dans le fichier `ecommerce/settings.py`, remplacez:

   ```python
   EMAIL_HOST_PASSWORD = 'okbb oobu kseu bcfo'  # Votre code actuel
   ```

   Par le NOUVEAU code de 16 caractères que Google vous a donné.

#### 4. Créer le code avec les espaces enlevés
   Si Google vous donne: `abcd efgh ijkl mnop`
   Utilisez: `abcdefghijklmnop`

   Dans `ecommerce/settings.py`:
   ```python
   EMAIL_HOST_PASSWORD = 'abcdefghijklmnop'  # Sans espaces
   ```

## 🔧 Configuration Actuelle

Votre configuration actuelle dans `ecommerce/settings.py`:

```python
EMAIL_HOST_USER = 'Matrixharck@gmail.com'
EMAIL_HOST_PASSWORD = 'okbb oobu kseu bcfo'
DEFAULT_FROM_EMAIL = 'Matrixharck@gmail.com'
```

## 🧪 Tester la Configuration

Pour tester si les emails fonctionnent, créez un compte test:

1. Allez sur http://127.0.0.1:8000/register/
2. Créez un compte
3. Un code de 6 chiffres devrait être envoyé à l'email que vous avez entré

## 📧 Types d'emails envoyés

Le site envoie automatiquement:

1. **Email de vérification** (après inscription)
   - Code à 6 chiffres
   - SENT par: `register()` dans `shop/views.py`

2. **Email de réinitialisation** (mot de passe oublié)
   - Lien de réinitialisation
   - SENT par: `forgot_password()` dans `shop/views.py`

## 🚨 Solutions aux Problèmes Courants

### Problème 1: "SMTPAuthenticationError"
**Cause**: Mot de passe d'application incorrect
**Solution**: Créez un nouveau mot de passe d'application sur https://myaccount.google.com/apppasswords

### Problème 2: "Connexion refusée"
**Cause**: Gmail bloque les connexions
**Solution**: Vérifiez que vous utilisez bien TLS (PORT 587)

### Problème 3: Pas de réponse du serveur
**Cause**: Problème réseau ou Gmail bloqué
**Solution**: 
   - Vérifiez votre connexion internet
   - Essayez depuis un autre réseau
   - Vérifiez que le port 587 n'est pas bloqué

### Problème 4: Emails dans spam
**Cause**: Normal pour les emails de développement
**Solution**: Vérifiez votre dossier spam/indésirables

## 🔐 Sécurité (IMPORTANT)

⚠️ **NE COMMITEZ JAMAIS** vos mots de passe dans Git!

Utilisez plutôt des variables d'environnement:

```python
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'Matrixharck@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'votre-mot-de-passe')
```

Puis créez un fichier `.env` (et ajoutez-le au `.gitignore`):
```
EMAIL_HOST_USER=Matrixharck@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe
```

## 📱 Alternative: Compte de Test

Si vous voulez tester rapidement SANS configurer Gmail:

Dans `ecommerce/settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

Cela affichera les emails dans la console au lieu de les envoyer. Utile pour le développement!

## ✅ Checklist

- [ ] Vérification en 2 étapes activée sur Google
- [ ] Mot de passe d'application créé
- [ ] Code de 16 caractères copié (sans espaces)
- [ ] Configuration mise à jour dans `settings.py`
- [ ] Test d'inscription effectué
- [ ] Email reçu dans la boîte de réception ou spam

## 📞 Besoin d'aide?

Si vous avez encore des problèmes, vérifiez:
1. Les logs Django dans la console
2. Votre dossier spam
3. Que le mot de passe d'application est correct (16 caractères sans espaces)

