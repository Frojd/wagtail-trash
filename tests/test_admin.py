from django.shortcuts import reverse
from django.test import TestCase
from wagtail.core.models import Page
from wagtail.tests.utils import WagtailTestUtils

from wagtail_trash.models import TrashCan, TrashCanPage
from wagtail_trash.views import trash_delete
from wagtail_trash.wagtail_hooks import TrashCanModelAdmin

trash_admin_url_helper = TrashCanModelAdmin().url_helper


class TestAdmin(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

    def test_visiting_bin_creates_one_if_not_exists(self):
        index_url = trash_admin_url_helper.get_action_url("index")

        assert TrashCanPage.objects.count() == 0

        resp = self.client.get(index_url)

        assert TrashCanPage.objects.count() == 1

        self.client.get(index_url)

    def test_buttons(self):
        root_page = Page.objects.get(url_path="/")

        top_page = Page(title="top_page")
        root_page.add_child(instance=top_page)

        sub_page = Page(title="sub_page")
        top_page.add_child(instance=sub_page)

        sub_sub_page = Page(title="sub_sub_page")
        sub_page.add_child(instance=sub_sub_page)

        with self.register_hook("before_delete_page", trash_delete):
            delete_url = reverse("wagtailadmin_pages:delete", args=(sub_sub_page.id,))
            self.client.post(delete_url)

            delete_url = reverse("wagtailadmin_pages:delete", args=(top_page.id,))
            self.client.post(delete_url)

        index = trash_admin_url_helper.get_action_url("index")
        resp = self.client.get(index)

        # Since sub_sub_pages parent is now in the trash can we should not show the "Restore"-button.
        self.assertFalse(
            reverse("wagtail_trash_restore", args=(sub_sub_page.id,))
            in str(resp.content)
        )
        self.assertTrue(
            reverse("wagtail_trash_move", args=(sub_sub_page.id,)) in str(resp.content)
        )

        # However - top page still has a parent (root) and should be able to be restored.
        self.assertTrue(
            reverse("wagtail_trash_restore", args=(top_page.id,)) in str(resp.content)
        )
        self.assertTrue(
            reverse("wagtail_trash_move", args=(top_page.id,)) in str(resp.content)
        )

    def test_removing_page_sends_it_to_trash_can(self):
        root_page = Page.objects.get(url_path="/")

        new_page = Page(title="new page")
        root_page.add_child(instance=new_page)

        assert TrashCan.objects.count() == 0

        with self.register_hook("before_delete_page", trash_delete):
            delete_url = reverse("wagtailadmin_pages:delete", args=(new_page.id,))
            self.client.post(delete_url)

        new_page = Page.objects.filter(title="new page")

        assert new_page.exists()
        assert new_page.child_of(TrashCanPage.objects.first())
        assert TrashCan.objects.count() == 1

    def test_removing_page_from_bin_deletes_it(self):
        root_page = Page.objects.get(url_path="/")

        new_page = Page(title="delete page")
        root_page.add_child(instance=new_page)

        with self.register_hook("before_delete_page", trash_delete):
            delete_url = reverse("wagtailadmin_pages:delete", args=(new_page.id,))
            self.client.post(delete_url)
            assert TrashCan.objects.count() == 1

            delete_url = reverse("wagtailadmin_pages:delete", args=(new_page.id,))
            self.client.post(delete_url)

        assert not Page.objects.filter(title="delete page")
        assert TrashCan.objects.count() == 0

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

        with self.register_hook("before_delete_page", trash_delete):
            delete_url = reverse("wagtailadmin_pages:delete", args=(top.id,))
            self.client.post(delete_url)

        top.refresh_from_db()

        self.assertEqual(top.get_descendants(inclusive=True).live().count(), 0)
        self.assertEqual(top.get_descendants(inclusive=True).not_live().count(), 4)

    def test_restoring_page_re_publishes(self):
        from wagtail_trash.wagtail_hooks import urlconf_time

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

        with self.register_hook("before_delete_page", trash_delete):
            delete_url = reverse("wagtailadmin_pages:delete", args=(top.id,))
            self.client.post(delete_url)

        top.refresh_from_db()

        self.assertEqual(top.get_descendants(inclusive=True).live().count(), 0)
        self.assertEqual(top.get_descendants(inclusive=True).not_live().count(), 4)

        with self.register_hook("register_admin_urls", urlconf_time):
            restore_url = reverse("wagtail_trash_restore", args=(top.id,))
            self.client.get(restore_url)

        top.refresh_from_db()

        self.assertEqual(top.get_descendants(inclusive=True).live().count(), 2)
        self.assertEqual(top.get_descendants(inclusive=True).not_live().count(), 2)
        self.assertEqual(TrashCan.objects.count(), 0)
        self.assertEqual(TrashCanPage.objects.first().get_children().count(), 0)

    def test_restoring_page_preserves_old_url(self):
        from wagtail_trash.wagtail_hooks import urlconf_time

        root_page = Page.objects.get(url_path="/home/")

        top = Page(title="1p", has_unpublished_changes=False, live=True)
        root_page.add_child(instance=top)

        sub_page = Page(title="1p 1u", has_unpublished_changes=True, live=False)
        top.add_child(instance=sub_page)

        sub_page = Page(title="1p 2p", has_unpublished_changes=False, live=True)
        top.add_child(instance=sub_page)

        original_top_url = top.url_path

        with self.register_hook("before_delete_page", trash_delete):
            delete_url = reverse("wagtailadmin_pages:delete", args=(top.id,))
            self.client.post(delete_url)

        top.refresh_from_db()

        self.assertNotEqual(original_top_url, top.url_path)

        with self.register_hook("register_admin_urls", urlconf_time):
            restore_url = reverse("wagtail_trash_restore", args=(top.id,))
            self.client.get(restore_url)

        top.refresh_from_db()

        self.assertEqual(original_top_url, top.url_path)

    def test_restoring_page_custom_move_to(self):
        from wagtail_trash.wagtail_hooks import urlconf_time

        root_page = Page.objects.get(url_path="/")

        top = Page(title="1p", has_unpublished_changes=False, live=True)
        root_page.add_child(instance=top)

        sub_page = Page(title="1p 1u", has_unpublished_changes=True, live=False)
        top.add_child(instance=sub_page)

        with self.register_hook("before_delete_page", trash_delete):
            delete_url = reverse("wagtailadmin_pages:delete", args=(sub_page.id,))
            self.client.post(delete_url)

        sub_page.refresh_from_db()

        with self.register_hook("register_admin_urls", urlconf_time):
            restore_url = reverse(
                "wagtail_trash_move",
                args=(sub_page.id,),
            )
            self.client.post(restore_url, {"move_page": str(root_page.id)})

        sub_page.refresh_from_db()

        self.assertIn(
            sub_page.id,
            list(root_page.get_children().values_list("id", flat=True)),
        )

        self.assertEqual(TrashCan.objects.count(), 0)

    def test_move_view_renders(self):
        from wagtail_trash.wagtail_hooks import urlconf_time

        root_page = Page.objects.get(url_path="/")

        top = Page(title="1p", has_unpublished_changes=False, live=True)
        root_page.add_child(instance=top)

        sub_page = Page(title="1p 1u", has_unpublished_changes=True, live=False)
        top.add_child(instance=sub_page)

        with self.register_hook("register_admin_urls", urlconf_time):
            restore_url = reverse(
                "wagtail_trash_move",
                args=(sub_page.id,),
            )
            self.client.get(restore_url)
