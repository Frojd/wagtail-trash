from django.core.management.base import BaseCommand

from wagtail_trash.models import TrashCan, TrashCanPage


class Command(BaseCommand):
    """
    Delete stray pages from recycle bin(s)

    Example:
        ./manage.py delete_stray_pages
    """

    def handle(self, *args, **options):
        trash_can_pages = TrashCanPage.objects.all()
        num_deleted_pages = 0
        for page in trash_can_pages:
            for child_page in page.get_children():
                if TrashCan.objects.filter(page=child_page).exists():
                    continue

                child_page.delete()
                num_deleted_pages += 1

        self.stdout.write("Deleted {} stray pages".format(num_deleted_pages))
