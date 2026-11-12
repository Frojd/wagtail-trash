from django.shortcuts import reverse
from django.test import TestCase, override_settings
from wagtail.models import Page, Site
from wagtail.test.utils import WagtailTestUtils

from tests.app.models import TestPage
from wagtail_trash.models import TrashCanPage


@override_settings(ALLOWED_HOSTS=["localhost", "other.test"])
class TestMultiSite(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()
        root = Page.objects.get(depth=1)
        self.home = Page.objects.get(url_path="/home/")
        self.other_home = root.add_child(instance=Page(title="other home"))
        Site.objects.create(hostname="other.test", port=80, root_page=self.other_home)

        self.page = self.home.add_child(instance=TestPage(title="page"))
        self.other_page = self.other_home.add_child(
            instance=TestPage(title="other page")
        )

    def trash(self, page, host):
        self.client.post(
            reverse("wagtailadmin_pages:delete", args=(page.id,)), HTTP_HOST=host
        )

    def test_each_site_gets_its_own_trash_can(self):
        self.trash(self.page, "localhost")
        self.trash(self.other_page, "other.test")

        self.assertEqual(TrashCanPage.objects.count(), 2)
        self.assertEqual(
            Page.objects.get(id=self.page.id).get_parent().get_parent().id,
            self.home.id,
        )
        self.assertEqual(
            Page.objects.get(id=self.other_page.id).get_parent().get_parent().id,
            self.other_home.id,
        )

    def test_trash_manager_excludes_pages_in_every_trash_can(self):
        kept = self.other_home.add_child(instance=TestPage(title="kept"))
        self.trash(self.page, "localhost")
        self.trash(self.other_page, "other.test")

        self.assertEqual(
            list(TestPage.objects_excluding_bins.values_list("id", flat=True)),
            [kept.id],
        )
