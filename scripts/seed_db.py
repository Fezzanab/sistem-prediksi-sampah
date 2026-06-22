"""Helper script to run database seeding without starting the full Flask server.

Usage:
  .\.venv\Scripts\Activate.ps1
  python scripts/seed_db.py

This will create the Flask app, initialize the DB (using your `DATABASE_URL` from .env),
and run the `seed_database()` routine defined in `app.py`. The seeding function is
idempotent so it won't duplicate records if they already exist.
"""
import logging
import importlib.util
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def load_app_module():
    """Load the project's app.py as a module to avoid name conflicts with installed packages named 'app'."""
    project_root = Path(__file__).resolve().parent.parent
    app_file = project_root / "app.py"
    if not app_file.exists():
        raise FileNotFoundError(f"Cannot find app.py at expected path: {app_file}")

    # Ensure project root is first on sys.path so local packages (models_db) are importable
    project_root_str = str(project_root)
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)

    spec = importlib.util.spec_from_file_location("project_app", str(app_file))
    module = importlib.util.module_from_spec(spec)
    loader = spec.loader
    if loader is None:
        raise ImportError("Could not load spec for app.py")
    loader.exec_module(module)
    return module


def main():
    module = load_app_module()
    create_app = getattr(module, "create_app", None)
    seed_database = getattr(module, "seed_database", None)
    if not create_app or not seed_database:
        raise ImportError("Loaded app.py does not expose 'create_app' and 'seed_database' functions")

    app = create_app()
    with app.app_context():
        try:
            seed_database()
            logging.info("Database seeding completed successfully.")
        except Exception as e:
            logging.exception("Database seeding failed: %s", e)


if __name__ == '__main__':
    main()
