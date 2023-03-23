from datetime import timedelta

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from wagtail.models import Page
from wagtail.test.utils import WagtailTestUtils

from wagtail_trash.models import TrashCan, TrashCanPage


class TestEmptyTrashCommand(TestCase, WagtailTestUtils):
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


class TestDeleteStraypagesCommand(TestCase, WagtailTestUtils):
    def test_delete_stray_pages_removes_pages_from_trash_can_witout_trashcan_association(
        self,
    ):
        root_page = Page.objects.get(url_path="/")

        trash_can_page = TrashCanPage(title="Trash can")
        root_page.add_child(instance=trash_can_page)

        new_page = Page(title="New page")
        trash_can_page.add_child(instance=new_page)
        TrashCan.objects.create(page=new_page)

        stray_page = Page(title="Stray page")
        trash_can_page.add_child(instance=stray_page)

        self.assertEqual(trash_can_page.get_children().count(), 2)

        call_command("delete_stray_pages")

        self.assertEqual(trash_can_page.get_children().count(), 1)
