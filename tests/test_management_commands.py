from datetime import timedelta, datetime
from django.core.management import call_command
from django.test import TestCase
from wagtail.tests.utils import WagtailTestUtils
from wagtail.core.models import Page
from wagtail_recycle_bin.models import RecycleBin


class TestManagementCommands(TestCase, WagtailTestUtils):
    def test_empty_bin_removes_pages_older_than_setting(self):
        root_page = Page.objects.get(url_path="/")

        new_page = Page(title="new page")
        root_page.add_child(instance=new_page)
        RecycleBin.objects.create(page=new_page)

        old_page = Page(title="new page oldie")
        root_page.add_child(instance=old_page)
        RecycleBin.objects.create(page=old_page)
        RecycleBin.objects.filter(page__title="new page oldie").update(
            time_recycled=datetime.now() - timedelta(days=31)
        )

        self.assertEqual(RecycleBin.objects.count(), 2)

        call_command("empty_recycle_bin", older_than_days=30)

        self.assertFalse(RecycleBin.objects.filter(page_id=old_page.id).exists())
        self.assertTrue(RecycleBin.objects.filter(page_id=new_page.id).exists())
        self.assertEqual(RecycleBin.objects.count(), 1)
