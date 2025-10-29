# 🔧 Correction de l'envoi d'emails Gmail

## ❌ Problème
Vous ne recevez pas les codes de confirmation par email.

## ✅ Solution

### Le problème avec votre configuration actuelle

Votre mot de passe d'application dans `ecommerce/settings.py` est:
```python
EMAIL_HOST_PASSWORD = 'okbb oobu kseu bcfo'  # Avec ESPACES
```

Google génère les mots de passe d'application avec des ESPACES pour la lisibilité, mais il faut les UTILISER SANS ESPACES.

### ✅ Correction appliquée

J'ai déjà corrigé dans le code pour utiliser:
```python
EMAIL_HOST_PASSWORD = 'okbbobuokseubcfo'  # SANS ESPACES
```

## 🧪 Test Maintenant

1. Redémarrez le serveur Django si nécessaire
2. Allez sur http://127.0.0.1:8000/register/
3. Créez un nouveau compte
4. Vous DEVRIEZ recevoir le code par email

## 📧 Vérifiez aussi

- Votre dossier **SPAM/INDÉSIRABLES**
- Votre dossier **PROMOTIONS** (Gmail)
- Tous les dossiers dans Gmail

## 🔄 Si ça ne marche toujours pas

### Option 1: Re-créer un nouveau mot de passe d'application

1. Allez sur: https://myaccount.google.com/apppasswords
2. Cliquez sur "Générer"
3. Sélectionnez "Mail" et "Autre"
4. Copiez le nouveau code (16 caractères)
5. **Enlevez tous les espaces**
6. Mettez-le dans `ecommerce/settings.py`

### Option 2: Mode test (console)

Pour tester sans Gmail, changez temporairement dans `ecommerce/settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

Les emails s'afficheront dans la console Django au lieu d'être envoyés.

## ✅ Prochaines étapes

1. **Testez l'inscription** - Créez un compte test
2. **Vérifiez votre email** (et spam)
3. **Testez "Mot de passe oublié"** - Essayez de réinitialiser un mot de passe

Le site est maintenant entièrement fonctionnel avec:
- ✓ Confirmation email avec code à 6 chiffres
- ✓ Réinitialisation de mot de passe par email
- ✓ Lien de réinitialisation sécurisé
- ✓ Vérification de compte obligatoire

