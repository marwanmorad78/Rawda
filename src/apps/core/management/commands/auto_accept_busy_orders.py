from django.core.management.base import BaseCommand

from apps.core.services import sync_center_status_and_auto_accept_waiting_orders


class Command(BaseCommand):
    help = "Accept orders that were waiting because the center was busy after busy_until expires."

    def handle(self, *args, **options):
        synced_count = sync_center_status_and_auto_accept_waiting_orders()
        self.stdout.write(self.style.SUCCESS(f"Synced {synced_count} orders."))
