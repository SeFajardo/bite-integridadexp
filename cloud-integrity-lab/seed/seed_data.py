"""
Wrapper around the `seed_data` management command.

The actual implementation lives in `reports/management/commands/seed_data.py`
so it can be invoked via:

    python manage.py seed_data

This module is kept for repository organization / discoverability.
"""
from reports.management.commands.seed_data import Command  # noqa: F401
