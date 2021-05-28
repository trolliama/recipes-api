import time

from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Command to wait for DB"""

    def handle(self, *args, **options):
        self.stdout.write("Waiting for database...")
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections["default"].cursor()
                # self.stdout.write("db_conn: {}".format(db_conn.cursor()))
            except OperationalError:
                self.stdout.write("Database not available")
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS("Database available"))
