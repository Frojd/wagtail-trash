from django.test import TestCase
from django.shortcuts import reverse
from wagtail.tests.utils import WagtailTestUtils
from wagtail.core.models import Page
from wagtail_recycle_bin.views import recycle_delete
from wagtail_recycle_bin.models import RecycleBinPage, RecycleBin
from wagtail_recycle_bin.wagtail_hooks import RecycleBinModelAdmin

recycle_admin_url_helper = RecycleBinModelAdmin().url_helper


class TestAdmin(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

    def test_visiting_bin_creates_one_if_not_exists(self):
        index_url = recycle_admin_url_helper.get_action_url("index")

        assert RecycleBinPage.objects.count() == 0

        resp = self.client.get(index_url)

        assert RecycleBinPage.objects.count() == 1

        self.client.get(index_url)

    def test_removing_page_sends_it_to_recycle_bin(self):
        root_page = Page.objects.get(url_path="/")

        new_page = Page(title="new page")
        root_page.add_child(instance=new_page)

        assert RecycleBin.objects.count() == 0

        with self.register_hook("before_delete_page", recycle_delete):
            delete_url = reverse("wagtailadmin_pages:delete", args=(new_page.id,))
            self.client.post(delete_url)

        new_page = Page.objects.filter(title="new page")

        assert new_page.exists()
        assert new_page.child_of(RecycleBinPage.objects.first())
        assert RecycleBin.objects.count() == 1

    def test_removing_page_from_bin_deletes_it(self):
        root_page = Page.objects.get(url_path="/")

        new_page = Page(title="delete page")
        root_page.add_child(instance=new_page)

        with self.register_hook("before_delete_page", recycle_delete):
            delete_url = reverse("wagtailadmin_pages:delete", args=(new_page.id,))
            self.client.post(delete_url)
            assert RecycleBin.objects.count() == 1

            delete_url = reverse("wagtailadmin_pages:delete", args=(new_page.id,))
            self.client.post(delete_url)

        assert not Page.objects.filter(title="delete page")
        assert RecycleBin.objects.count() == 0

    def test_removing_page_unpublishes_all_sub_pages(self):
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

        self.assertEqual(top.get_descendants(inclusive=True).live().count(), 2)
        self.assertEqual(top.get_descendants(inclusive=True).not_live().count(), 2)

        with self.register_hook("before_delete_page", recycle_delete):
            delete_url = reverse("wagtailadmin_pages:delete", args=(top.id,))
            self.client.post(delete_url)

        top.refresh_from_db()

        self.assertEqual(top.get_descendants(inclusive=True).live().count(), 0)
        self.assertEqual(top.get_descendants(inclusive=True).not_live().count(), 4)

    def test_restoring_page_re_publishes(self):
        from wagtail_recycle_bin.wagtail_hooks import urlconf_time

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

        self.assertEqual(top.get_descendants(inclusive=True).live().count(), 2)
        self.assertEqual(top.get_descendants(inclusive=True).not_live().count(), 2)

        with self.register_hook("before_delete_page", recycle_delete):
            delete_url = reverse("wagtailadmin_pages:delete", args=(top.id,))
            self.client.post(delete_url)

        top.refresh_from_db()

        self.assertEqual(top.get_descendants(inclusive=True).live().count(), 0)
        self.assertEqual(top.get_descendants(inclusive=True).not_live().count(), 4)

        with self.register_hook("register_admin_urls", urlconf_time):
            restore_url = reverse("wagtail_recycle_bin_restore", args=(top.id,))
            self.client.post(restore_url)

        top.refresh_from_db()

        self.assertEqual(top.get_descendants(inclusive=True).live().count(), 2)
        self.assertEqual(top.get_descendants(inclusive=True).not_live().count(), 2)
        self.assertEqual(RecycleBin.objects.count(), 0)
        self.assertEqual(RecycleBinPage.objects.first().get_children().count(), 0)
