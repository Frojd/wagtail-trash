from django.shortcuts import reverse
from django.test import TestCase
from wagtail.models import Page
from wagtail.test.utils import WagtailTestUtils

from tests.app.models import TestPage
from wagtail_trash.views import trash_delete


class TestManagers(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

    def test_manager(self):
        from wagtail_trash.wagtail_hooks import urlconf_time

        root_page = Page.objects.get(url_path="/")

        top_page = TestPage(title="top_page")
        root_page.add_child(instance=top_page)

        sub_page = TestPage(title="sub_page")
        top_page.add_child(instance=sub_page)

        sub_sub_page = TestPage(title="sub_sub_page")
        sub_page.add_child(instance=sub_sub_page)

        self.assertEqual(TestPage.objects.count(), 3)
        self.assertEqual(TestPage.objects_excluding_bins.count(), 3)

        with self.register_hook("before_delete_page", trash_delete):
            delete_url = reverse("wagtailadmin_pages:delete", args=(sub_sub_page.id,))
            self.client.post(delete_url)

        self.assertEqual(TestPage.objects.count(), 3)
        self.assertEqual(TestPage.objects_excluding_bins.count(), 2)

        with self.register_hook("register_admin_urls", urlconf_time):
            restore_url = reverse("wagtail_trash_restore", args=(sub_sub_page.id,))
            self.client.get(restore_url)

        self.assertEqual(TestPage.objects.count(), 3)
        self.assertEqual(TestPage.objects_excluding_bins.count(), 3)

        with self.register_hook("before_delete_page", trash_delete):
            delete_url = reverse("wagtailadmin_pages:delete", args=(top_page.id,))
            self.client.post(delete_url)

        self.assertEqual(TestPage.objects.count(), 3)
        self.assertEqual(TestPage.objects_excluding_bins.count(), 0)
