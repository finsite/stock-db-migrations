"""Main entry point for DB migrations."""

import os
import sys

# Add 'src/' to module search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db_migrator import run_migration
from app.utils.setup_logger import setup_logger

logger = setup_logger(__name__)


def main() -> None:
    logger.info("🚀 Starting DB migration...")
    run_migration()
    logger.info("✅ Migration complete.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception("❌ Unhandled exception in main: %s", e)
        sys.exit(1)
