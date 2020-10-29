from datetime import timedelta, datetime
from django.core.management.base import BaseCommand
from wagtail_trash.models import TrashCan


class Command(BaseCommand):
    """
    Remove pages from recycle bin

    Example:
        ./manage.py empty_trash --older_than_days=30

    Will remove all pages that were deleted more than 30 days ago
    """

    def add_arguments(self, parser):
        parser.add_argument("--older_than_days", required=True)

    def handle(self, *args, **options):
        days = int(options["older_than_days"])

        removal_date = datetime.now() - timedelta(days=days)

        rbs = TrashCan.objects.filter(time_recycled__lt=removal_date)

        for rb in rbs:
            rb.page.delete()
