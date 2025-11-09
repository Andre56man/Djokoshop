import argparse
import os
import subprocess
import sys


CATEGORIES = {
    "all": ["shop.tests"],
    "unit": [
        "shop.tests.test_models",
        "shop.tests.test_forms",
        "shop.tests.test_permissions",
        "shop.tests.test_auth",
        "shop.tests.test_context_processors",
    ],
    "integration": [
        "shop.tests.test_integration",
        "shop.tests.test_payment_integration",
    ],
    "views": ["shop.tests.test_views"],
    "models": ["shop.tests.test_models"],
    "forms": ["shop.tests.test_forms"],
    "security": ["shop.tests.test_security"],
    "payment": ["shop.tests.test_payment_integration"],
}


def run_tests(modules, verbosity=2):
    if not os.path.exists("manage.py"):
        print("[ERROR] manage.py not found. Run this script from the Djokoshop project root.")
        sys.exit(1)
    cmd = [sys.executable, "manage.py", "test", *modules, "-v", str(verbosity)]
    print("[RUN]", " ".join(cmd))
    try:
        return subprocess.call(cmd)
    except KeyboardInterrupt:
        print("Interrupted.")
        return 130


def main():
    parser = argparse.ArgumentParser(description="Run Django tests by category")
    parser.add_argument("category", nargs="?", default="all", help=f"One of: {', '.join(CATEGORIES.keys())}")
    parser.add_argument("specific", nargs="*", help="Specific test modules or test labels to run")
    parser.add_argument("-v", "--verbosity", type=int, default=2, help="Verbosity level (0-3)")
    args = parser.parse_args()

    if args.specific:
        modules = args.specific
    else:
        modules = CATEGORIES.get(args.category.lower(), CATEGORIES["all"])

    exit_code = run_tests(modules, verbosity=args.verbosity)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()