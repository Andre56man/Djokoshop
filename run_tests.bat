@echo off
REM Simple helper pour exécuter les tests Django
SETLOCAL ENABLEDELAYEDEXPANSION

set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

if not exist manage.py (
  echo [ERREUR] manage.py introuvable dans %PROJECT_DIR%
  echo Placez ce script a la racine du projet Djokoshop.
  exit /b 1
)

set TARGET=%1
if "%TARGET%"=="" (
  echo.
  echo [Tous les tests] django test shop.tests -v 2
  python manage.py test shop.tests -v 2
  goto end
)

if /I "%TARGET%"=="all" (
  echo [Tous les tests]
  python manage.py test shop.tests -v 2
  goto end
)
if /I "%TARGET%"=="unit" (
  echo [Unit Tests]
  python manage.py test ^
    shop.tests.test_models ^
    shop.tests.test_forms ^
    shop.tests.test_permissions ^
    shop.tests.test_auth ^
    shop.tests.test_context_processors ^
    -v 2
  goto end
)
if /I "%TARGET%"=="integration" (
  echo [Integration Tests]
  python manage.py test ^
    shop.tests.test_integration ^
    shop.tests.test_payment_integration ^
    -v 2
  goto end
)
if /I "%TARGET%"=="views" (
  echo [Views Tests]
  python manage.py test shop.tests.test_views -v 2
  goto end
)
if /I "%TARGET%"=="models" (
  echo [Models Tests]
  python manage.py test shop.tests.test_models -v 2
  goto end
)
if /I "%TARGET%"=="forms" (
  echo [Forms Tests]
  python manage.py test shop.tests.test_forms -v 2
  goto end
)
if /I "%TARGET%"=="security" (
  echo [Security/Permissions Tests]
  python manage.py test shop.tests.test_security -v 2
  goto end
)
if /I "%TARGET%"=="payment" (
  echo [Payment Integration Tests]
  python manage.py test shop.tests.test_payment_integration -v 2
  goto end
)

echo [Info] Categorie inconnue: %TARGET%
echo Utilisation: run_tests.bat [all|unit|integration|views|models|forms|security|payment]
python manage.py test shop.tests -v 2

:end
ENDLOCAL