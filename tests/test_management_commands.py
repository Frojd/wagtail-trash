from datetime import timedelta

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from wagtail.core.models import Page
from wagtail.tests.utils import WagtailTestUtils

from wagtail_trash.models import TrashCan


class TestManagementCommands(TestCase, WagtailTestUtils):
    def test_empty_bin_removes_pages_older_than_setting(self):
        root_page = Page.objects.get(url_path="/")

        new_page = Page(title="new page")
        root_page.add_child(instance=new_page)
        TrashCan.objects.create(page=new_page)

        old_page = Page(title="new page oldie")
        root_page.add_child(instance=old_page)
        TrashCan.objects.create(page=old_page)
        TrashCan.objects.filter(page__title="new page oldie").update(
            time_recycled=timezone.now() - timedelta(days=31)
        )

        self.assertEqual(TrashCan.objects.count(), 2)

        call_command("empty_trash", older_than_days=30)

        self.assertFalse(TrashCan.objects.filter(page_id=old_page.id).exists())
        self.assertTrue(TrashCan.objects.filter(page_id=new_page.id).exists())
        self.assertEqual(TrashCan.objects.count(), 1)
