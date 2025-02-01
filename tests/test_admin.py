from django.shortcuts import reverse
from django.test import TestCase
from wagtail.models import Page
from wagtail.test.utils import WagtailTestUtils

from wagtail_trash.models import TrashCan, TrashCanPage
from wagtail_trash.views import trash_bulk_delete, trash_delete
from wagtail_trash.wagtail_hooks import TrashCanModelAdmin

trash_admin_url_helper = TrashCanModelAdmin().url_helper


class TestAdmin(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

    def test_visiting_bin_creates_one_if_not_exists(self):
        index_url = trash_admin_url_helper.get_action_url("index")

        assert TrashCanPage.objects.count() == 0

        self.client.get(index_url)

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

    def test_bulk_delete_sets_and_unsets_slug(self):
        from wagtail_trash.wagtail_hooks import urlconf_time

        root_page = Page.objects.get(url_path="/")

        new_page1 = Page(title="new page 1")

        p1 = root_page.add_child(instance=new_page1)

        p1_slug = p1.slug

        with self.register_hook("before_bulk_action", trash_bulk_delete):
            delete_url = reverse(
                "wagtail_bulk_action", args=("wagtailcore", "page", "delete")
            )
            id_query = "?id=" + "&id=".join([str(p1.id)])
            self.client.post(delete_url + id_query)

        p1.refresh_from_db()
        self.assertEqual(f"trash-{p1.pk}-{p1_slug}", p1.slug)

        with self.register_hook("register_admin_urls", urlconf_time):
            restore_url = reverse("wagtail_trash_restore", args=(p1.pk,))
            self.client.get(restore_url)

        p1.refresh_from_db()
        self.assertEqual(p1_slug, p1.slug)

    def test_bulk_delete_sends_to_trash_can(self):
        root_page = Page.objects.get(url_path="/")

        new_page1 = Page(title="new page 1")
        new_page2 = Page(title="new page 2")
        new_page3 = Page(title="new page 3")
        new_page4 = Page(title="new page 4")

        p1 = root_page.add_child(instance=new_page1)
        p2 = root_page.add_child(instance=new_page2)
        p3 = root_page.add_child(instance=new_page3)
        p4 = root_page.add_child(instance=new_page4)

        assert TrashCan.objects.count() == 0

        with self.register_hook("before_bulk_action", trash_bulk_delete):
            delete_url = reverse(
                "wagtail_bulk_action", args=("wagtailcore", "page", "delete")
            )
            id_query = "?id=" + "&id=".join(
                [str(p1.id), str(p2.id), str(p3.id), str(p4.id)]
            )
            self.client.post(delete_url + id_query)

        assert TrashCan.objects.count() == 4

    def test_removing_page_from_bin_deletes_it(self):
        root_page = Page.objects.get(url_path="/")

        new_page = Page(title="delete page")
        root_page.add_child(instance=new_page)

        with self.register_hook("before_delete_page", trash_delete):
            delete_url = reverse("wagtailadmin_pages:delete", args=(new_page.id,))
            self.client.post(delete_url)
            assert TrashCan.objects.count() == 1

            trash_can_item = TrashCan.objects.first()
            delete_url = trash_admin_url_helper.get_action_url(
                "delete",
                trash_can_item.id,
            )
            self.client.post(delete_url)
            assert not Page.objects.filter(title="delete page")
            assert TrashCan.objects.count() == 0

    def test_removing_two_pages_with_same_slug(self):
        root_page = Page.objects.get(url_path="/")

        cat = Page(title="category 1", slug="category-1")
        cat_instance = root_page.add_child(instance=cat)
        cat_2 = Page(title="category 2", slug="category-2")
        cat_instance_2 = root_page.add_child(instance=cat_2)

        delete = Page(title="delete", slug="delete")
        cat_instance.add_child(instance=delete)
        delete_2 = Page(title="delete", slug="delete")
        cat_instance_2.add_child(instance=delete_2)

        with self.register_hook("before_delete_page", trash_delete):
            delete_url = reverse("wagtailadmin_pages:delete", args=(delete.id,))
            self.client.post(delete_url)
            delete_url = reverse("wagtailadmin_pages:delete", args=(delete_2.id,))
            self.client.post(delete_url)

            self.assertEqual(TrashCan.objects.count(), 2)

    def test_removing_page_unpublishes_all_sub_pages(self):
        root_page = Page.objects.get(url_path="/")

        top = Page(title="1p", has_unpublished_changes=False, live=True)
        root_page.add_child(instance=top)

        sub_page = Page(title="1p 1u", has_unpublished_changes=True, live=False)
        top.add_child(instance=sub_page)

        sub_page = Page(title="1p 2p", has_unpublished_changes=False, live=True)
        top.add_child(instance=sub_page)

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

    def test_restoring_page_custom_move_to_without_id_returns_validation_error(self):
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
            response = self.client.post(restore_url, {"move_page": ""})
            self.assertIn("This field is required", str(response.content))

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
