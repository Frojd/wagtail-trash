from django.shortcuts import reverse
from django.test import TestCase
from wagtail.models import Page
from wagtail.test.utils import WagtailTestUtils

from tests.app.models import TestPage
from tests.utils import trash_page


class TestManagers(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

    def test_manager(self):
        root_page = Page.objects.get(url_path="/")

        top_page = TestPage(title="top_page")
        root_page.add_child(instance=top_page)

        sub_page = TestPage(title="sub_page")
        top_page.add_child(instance=sub_page)

        sub_sub_page = TestPage(title="sub_sub_page")
        sub_page.add_child(instance=sub_sub_page)

        self.assertEqual(TestPage.objects.count(), 3)
        self.assertEqual(TestPage.objects_excluding_bins.count(), 3)

        trash_page(self.client, sub_sub_page)

        self.assertEqual(TestPage.objects.count(), 3)
        self.assertEqual(TestPage.objects_excluding_bins.count(), 2)

        restore_url = reverse("wagtail_trash_restore", args=(sub_sub_page.id,))
        self.client.post(restore_url)

        self.assertEqual(TestPage.objects.count(), 3)
        self.assertEqual(TestPage.objects_excluding_bins.count(), 3)

        trash_page(self.client, top_page)

        self.assertEqual(TestPage.objects.count(), 3)
        self.assertEqual(TestPage.objects_excluding_bins.count(), 0)
