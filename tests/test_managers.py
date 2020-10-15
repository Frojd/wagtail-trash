from django.test import TestCase
from django.shortcuts import reverse
from wagtail.tests.utils import WagtailTestUtils
from wagtail.core.models import Page
from wagtail_recycle_bin.views import recycle_delete
from wagtail_recycle_bin.models import RecycleBinPage, RecycleBin
from wagtail_recycle_bin.wagtail_hooks import RecycleBinModelAdmin
from tests.app.models import TestPage

recycle_admin_url_helper = RecycleBinModelAdmin().url_helper


class TestManagers(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

    def test_manager(self):
        from wagtail_recycle_bin.wagtail_hooks import urlconf_time

        root_page = Page.objects.get(url_path="/")

        top_page = TestPage(title="top_page")
        root_page.add_child(instance=top_page)

        sub_page = TestPage(title="sub_page")
        top_page.add_child(instance=sub_page)

        sub_sub_page = TestPage(title="sub_sub_page")
        sub_page.add_child(instance=sub_sub_page)

        self.assertEquals(TestPage.objects.count(), 3)
        self.assertEquals(TestPage.objects_excluding_bins.count(), 3)

        with self.register_hook("before_delete_page", recycle_delete):
            delete_url = reverse("wagtailadmin_pages:delete", args=(sub_sub_page.id,))
            self.client.post(delete_url)

        self.assertEquals(TestPage.objects.count(), 3)
        self.assertEquals(TestPage.objects_excluding_bins.count(), 2)

        with self.register_hook("register_admin_urls", urlconf_time):
            restore_url = reverse(
                "wagtail_recycle_bin_restore", args=(sub_sub_page.id,)
            )
            self.client.get(restore_url)

        self.assertEquals(TestPage.objects.count(), 3)
        self.assertEquals(TestPage.objects_excluding_bins.count(), 3)

        with self.register_hook("before_delete_page", recycle_delete):
            delete_url = reverse("wagtailadmin_pages:delete", args=(top_page.id,))
            self.client.post(delete_url)

        self.assertEquals(TestPage.objects.count(), 3)
        self.assertEquals(TestPage.objects_excluding_bins.count(), 0)
