from django.shortcuts import reverse
from django.test import TestCase
from wagtail.models import Page
from wagtail.test.utils import WagtailTestUtils

from tests.app.models import TestPage
from tests.utils import trash_page


class TestSkipSitemapIfInTrashMixin(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()
        home = Page.objects.get(url_path="/home/")
        self.page = home.add_child(instance=TestPage(title="page"))
        self.child = self.page.add_child(instance=TestPage(title="child"))

    def test_descendants_of_trashed_page_have_no_sitemap_urls(self):
        self.assertNotEqual(self.child.get_sitemap_urls(), [])

        trash_page(self.client, self.page)

        self.assertEqual(TestPage.objects.get(id=self.child.id).get_sitemap_urls(), [])

    def test_descendants_have_sitemap_urls_after_restore(self):
        trash_page(self.client, self.page)
        self.client.post(reverse("wagtail_trash_restore", args=(self.page.id,)))

        self.assertNotEqual(
            TestPage.objects.get(id=self.child.id).get_sitemap_urls(), []
        )
