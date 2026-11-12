import json

from django.shortcuts import reverse
from django.test import TestCase
from wagtail.models import Page
from wagtail.test.utils import WagtailTestUtils

from tests.utils import trash_page
from wagtail_trash.models import TrashCanPage


class TestHiddenTrashCan(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()
        self.home = Page.objects.get(url_path="/home/")
        self.sibling = self.home.add_child(instance=Page(title="sibling"))
        page = self.home.add_child(instance=Page(title="page"))
        trash_page(self.client, page)
        self.trash_can = TrashCanPage.objects.get()
        self.assertEqual(self.trash_can.get_parent().id, self.home.id)

    def test_explorer_hides_trash_can(self):
        response = self.client.get(
            reverse("wagtailadmin_explore", args=(self.home.id,))
        )

        self.assertContains(
            response, reverse("wagtailadmin_pages:edit", args=(self.sibling.id,))
        )
        self.assertNotContains(response, f"/admin/pages/{self.trash_can.id}/")

    def test_page_chooser_hides_trash_can(self):
        response = self.client.get(
            reverse("wagtailadmin_choose_page_child", args=(self.home.id,))
        )
        html = json.loads(response.content)["html"]

        self.assertIn(f'data-id="{self.sibling.id}"', html)
        self.assertNotIn(f'data-id="{self.trash_can.id}"', html)
