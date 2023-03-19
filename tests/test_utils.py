import json

from django.test import TestCase
from wagtail.models import Page
from wagtail.test.utils import WagtailTestUtils

from wagtail_trash.utils import generate_page_data


class TestUtils(TestCase, WagtailTestUtils):
    def test_generate_page_data(self):
        root_page = Page.objects.get(url_path="/")

        top = Page(title="1p", has_unpublished_changes=False, live=True)
        root_page.add_child(instance=top)

        sub_page = Page(title="1p 1u", has_unpublished_changes=True, live=False)
        top.add_child(instance=sub_page)

        sub_page = Page(title="1p 2p", has_unpublished_changes=False, live=True)
        top.add_child(instance=sub_page)
        sub_page_id = sub_page.id

        sub_sub_page = Page(title="1p 2p 3u", has_unpublished_changes=True, live=False)
        sub_page.add_child(instance=sub_sub_page)

        self.assertEqual(top.get_descendants().live().count(), 1)
        self.assertEqual(top.get_descendants().not_live().count(), 2)

        self.assertEqual(
            json.loads(generate_page_data(top)), {"published": [top.id, sub_page_id]}
        )
