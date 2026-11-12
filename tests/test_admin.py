from django.contrib.messages import get_messages
from django.shortcuts import reverse
from django.test import TestCase
from wagtail.models import Page
from wagtail.test.utils import WagtailTestUtils

from tests.app.models import ArticlePage, SectionPage, SingletonPage, TestPage
from tests.utils import trash_page
from wagtail_trash.models import TrashCan, TrashCanPage
from wagtail_trash.wagtail_hooks import TrashCanModelAdmin

trash_admin_url_helper = TrashCanModelAdmin().url_helper


class TestAdmin(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

    def test_visiting_bin_creates_one_if_not_exists(self):
        index_url = trash_admin_url_helper.get_action_url("index")

        assert TrashCanPage.objects.count() == 0

        self.client.get(index_url)

        trash_can = TrashCanPage.objects.get()
        self.assertEqual(trash_can.get_parent().url_path, "/home/")
        self.assertFalse(trash_can.live)

        self.client.get(index_url)

        self.assertEqual(TrashCanPage.objects.get().id, trash_can.id)

    def test_buttons(self):
        root_page = Page.objects.get(url_path="/")

        top_page = Page(title="top_page")
        root_page.add_child(instance=top_page)

        sub_page = Page(title="sub_page")
        top_page.add_child(instance=sub_page)

        sub_sub_page = Page(title="sub_sub_page")
        sub_page.add_child(instance=sub_sub_page)

        trash_page(self.client, sub_sub_page)

        trash_page(self.client, top_page)

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

    def test_index_escapes_page_titles(self):
        home = Page.objects.get(url_path="/home/")
        parent = home.add_child(instance=Page(title="<script>alert(1)</script>"))
        parent.add_child(instance=Page(title="<img src=x onerror=alert(2)>"))

        trash_page(self.client, parent)

        content = self.client.get(
            trash_admin_url_helper.get_action_url("index")
        ).content.decode()

        self.assertNotIn("<script>alert(1)</script>", content)
        self.assertNotIn("<img src=x onerror=alert(2)>", content)
        self.assertIn(
            "<strong>&lt;script&gt;alert(1)&lt;/script&gt;</strong><br>"
            "&nbsp;&lt;img src=x onerror=alert(2)&gt;<br>",
            content,
        )

    def test_removing_page_sends_it_to_trash_can(self):
        root_page = Page.objects.get(url_path="/")

        new_page = Page(title="new page")
        root_page.add_child(instance=new_page)

        assert TrashCan.objects.count() == 0

        trash_page(self.client, new_page)

        new_page = Page.objects.filter(title="new page")

        assert new_page.exists()
        assert new_page.child_of(TrashCanPage.objects.first())
        assert TrashCan.objects.count() == 1

    def test_trash_can_and_children_are_not_indexed_in_sitemap(self):
        root_page = Page.objects.get(url_path="/")

        new_page = TestPage(title="new page")
        root_page.add_child(instance=new_page)

        assert len(new_page.get_sitemap_urls()) != 0

        trash_page(self.client, new_page)

        trash_can_page = TrashCanPage.objects.first()
        new_page.refresh_from_db()
        assert len(trash_can_page.get_sitemap_urls()) == 0
        assert len(new_page.get_sitemap_urls()) == 0

    def test_bulk_delete_sets_and_unsets_slug(self):
        root_page = Page.objects.get(url_path="/")

        new_page1 = Page(title="new page 1")

        p1 = root_page.add_child(instance=new_page1)

        p1_slug = p1.slug

        delete_url = reverse(
            "wagtail_bulk_action", args=("wagtailcore", "page", "delete")
        )
        id_query = "?id=" + "&id=".join([str(p1.id)])
        self.client.post(delete_url + id_query)

        p1.refresh_from_db()
        self.assertEqual(f"trash-{p1.pk}-{p1_slug}", p1.slug)

        restore_url = reverse("wagtail_trash_restore", args=(p1.pk,))
        self.client.post(restore_url)

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

        trash_page(self.client, new_page)
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

        trash_page(self.client, delete)
        trash_page(self.client, delete_2)

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

        trash_page(self.client, top)

        top.refresh_from_db()

        self.assertEqual(top.get_descendants(inclusive=True).live().count(), 0)
        self.assertEqual(top.get_descendants(inclusive=True).not_live().count(), 4)

    def test_restoring_page_re_publishes(self):
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

        trash_page(self.client, top)

        top.refresh_from_db()

        self.assertEqual(top.get_descendants(inclusive=True).live().count(), 0)
        self.assertEqual(top.get_descendants(inclusive=True).not_live().count(), 4)

        restore_url = reverse("wagtail_trash_restore", args=(top.id,))
        self.client.post(restore_url)

        top.refresh_from_db()

        self.assertEqual(top.get_descendants(inclusive=True).live().count(), 2)
        self.assertEqual(top.get_descendants(inclusive=True).not_live().count(), 2)
        self.assertEqual(TrashCan.objects.count(), 0)
        self.assertEqual(TrashCanPage.objects.first().get_children().count(), 0)

    def test_restoring_page_preserves_old_url(self):
        root_page = Page.objects.get(url_path="/home/")

        top = Page(title="1p", has_unpublished_changes=False, live=True)
        root_page.add_child(instance=top)

        sub_page = Page(title="1p 1u", has_unpublished_changes=True, live=False)
        top.add_child(instance=sub_page)

        sub_page = Page(title="1p 2p", has_unpublished_changes=False, live=True)
        top.add_child(instance=sub_page)

        original_top_url = top.url_path

        trash_page(self.client, top)

        top.refresh_from_db()

        self.assertNotEqual(original_top_url, top.url_path)

        restore_url = reverse("wagtail_trash_restore", args=(top.id,))
        self.client.post(restore_url)

        top.refresh_from_db()

        self.assertEqual(original_top_url, top.url_path)

    def test_restoring_page_custom_move_to(self):
        root_page = Page.objects.get(url_path="/")

        top = Page(title="1p", has_unpublished_changes=False, live=True)
        root_page.add_child(instance=top)

        sub_page = Page(title="1p 1u", has_unpublished_changes=True, live=False)
        top.add_child(instance=sub_page)

        trash_page(self.client, sub_page)

        sub_page.refresh_from_db()

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
        root_page = Page.objects.get(url_path="/")

        top = Page(title="1p", has_unpublished_changes=False, live=True)
        root_page.add_child(instance=top)

        sub_page = Page(title="1p 1u", has_unpublished_changes=True, live=False)
        top.add_child(instance=sub_page)

        trash_page(self.client, sub_page)

        sub_page.refresh_from_db()

        restore_url = reverse(
            "wagtail_trash_move",
            args=(sub_page.id,),
        )
        response = self.client.post(restore_url, {"move_page": ""})
        self.assertIn("This field is required", str(response.content))

    def test_restore_with_deleted_parent_redirects_to_move(self):
        home = Page.objects.get(url_path="/home/")
        parent = home.add_child(instance=Page(title="parent"))
        child = parent.add_child(instance=Page(title="child"))

        trash_page(self.client, child)
        Page.objects.get(id=parent.id).delete()

        response = self.client.post(reverse("wagtail_trash_restore", args=(child.id,)))

        self.assertRedirects(
            response,
            reverse("wagtail_trash_move", args=(child.id,)),
            fetch_redirect_response=False,
        )
        self.assertEqual(
            [m.level_tag for m in get_messages(response.wsgi_request)][-1], "error"
        )
        self.assertTrue(TrashCan.objects.filter(page_id=child.id).exists())

    def test_restore_with_slug_conflict_keeps_page_in_trash(self):
        home = Page.objects.get(url_path="/home/")
        page = home.add_child(instance=Page(title="page", slug="page"))

        trash_page(self.client, page)
        home.add_child(instance=Page(title="replacement", slug="page"))

        response = self.client.post(reverse("wagtail_trash_restore", args=(page.id,)))

        self.assertRedirects(
            response,
            reverse("wagtail_trash_move", args=(page.id,)),
            fetch_redirect_response=False,
        )
        self.assertEqual(
            [m.level_tag for m in get_messages(response.wsgi_request)][-1], "error"
        )
        page.refresh_from_db()
        self.assertEqual(page.slug, f"trash-{page.id}-page")
        self.assertEqual(page.get_parent().specific_class, TrashCanPage)
        self.assertTrue(TrashCan.objects.filter(page_id=page.id).exists())

    def test_restore_and_move_with_slug_conflict_shows_form_error(self):
        home = Page.objects.get(url_path="/home/")
        page = home.add_child(instance=Page(title="page", slug="page"))
        trash_page(self.client, page)

        destination = home.add_child(instance=Page(title="destination"))
        destination.add_child(instance=Page(title="occupant", slug="page"))

        response = self.client.post(
            reverse("wagtail_trash_move", args=(page.id,)),
            {"move_page": str(destination.id)},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "move_page",
            "The slug 'page' is already in use at the destination.",
        )
        page.refresh_from_db()
        self.assertEqual(page.slug, f"trash-{page.id}-page")
        self.assertTrue(TrashCan.objects.filter(page_id=page.id).exists())

    def test_restore_into_trashed_parent_is_rejected(self):
        home = Page.objects.get(url_path="/home/")
        parent = home.add_child(instance=Page(title="parent"))
        child = parent.add_child(instance=Page(title="child"))

        trash_page(self.client, child)
        trash_page(self.client, parent)

        response = self.client.post(reverse("wagtail_trash_restore", args=(child.id,)))

        self.assertRedirects(
            response,
            reverse("wagtail_trash_move", args=(child.id,)),
            fetch_redirect_response=False,
        )
        self.assertEqual(
            [m.level_tag for m in get_messages(response.wsgi_request)][-1], "error"
        )
        child.refresh_from_db()
        self.assertEqual(child.get_parent().specific_class, TrashCanPage)
        self.assertTrue(TrashCan.objects.filter(page_id=child.id).exists())

    def test_restore_and_move_into_trashed_page_shows_form_error(self):
        home = Page.objects.get(url_path="/home/")
        page = home.add_child(instance=Page(title="page"))
        trashed_section = home.add_child(instance=Page(title="trashed section"))
        destination = trashed_section.add_child(instance=Page(title="destination"))

        trash_page(self.client, page)
        trash_page(self.client, trashed_section)

        response = self.client.post(
            reverse("wagtail_trash_move", args=(page.id,)),
            {"move_page": str(destination.id)},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "move_page",
            "The destination is in the trash can, choose another location.",
        )
        page.refresh_from_db()
        self.assertEqual(page.get_parent().specific_class, TrashCanPage)
        self.assertTrue(TrashCan.objects.filter(page_id=page.id).exists())

    def test_restore_and_move_with_unknown_destination_shows_form_error(self):
        home = Page.objects.get(url_path="/home/")
        page = home.add_child(instance=Page(title="page"))
        trash_page(self.client, page)

        response = self.client.post(
            reverse("wagtail_trash_move", args=(page.id,)),
            {"move_page": "999999"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "move_page", "The chosen page does not exist."
        )
        self.assertTrue(TrashCan.objects.filter(page_id=page.id).exists())

    def test_move_view_renders_destination_form(self):
        home = Page.objects.get(url_path="/home/")
        page = home.add_child(instance=Page(title="page"))
        trash_page(self.client, page)

        response = self.client.get(reverse("wagtail_trash_move", args=(page.id,)))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="move_page"')
        self.assertContains(response, "csrfmiddlewaretoken")
        self.assertTrue(TrashCan.objects.filter(page_id=page.id).exists())

    def test_move_view_includes_editor_js_hook_output(self):
        home = Page.objects.get(url_path="/home/")
        page = home.add_child(instance=Page(title="page"))
        trash_page(self.client, page)

        marker = '<script src="/editor-js-hook-marker.js"></script>'

        with self.register_hook("insert_editor_js", lambda: marker):
            response = self.client.get(reverse("wagtail_trash_move", args=(page.id,)))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode().count(marker), 1)

    def test_restore_get_shows_confirmation_without_restoring(self):
        home = Page.objects.get(url_path="/home/")
        page = home.add_child(instance=Page(title="page", slug="page"))
        trash_page(self.client, page)
        restore_url = reverse("wagtail_trash_restore", args=(page.id,))

        response = self.client.get(restore_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'action="{restore_url}" method="POST"')
        self.assertContains(response, "csrfmiddlewaretoken")
        page.refresh_from_db()
        self.assertEqual(page.get_parent().specific_class, TrashCanPage)
        self.assertTrue(TrashCan.objects.filter(page_id=page.id).exists())

    def test_restore_post_restores_page(self):
        home = Page.objects.get(url_path="/home/")
        page = home.add_child(instance=Page(title="page", slug="page"))
        trash_page(self.client, page)

        response = self.client.post(reverse("wagtail_trash_restore", args=(page.id,)))

        self.assertRedirects(
            response,
            reverse("wagtailadmin_explore", args=(page.id,)),
            fetch_redirect_response=False,
        )
        page.refresh_from_db()
        self.assertEqual(page.get_parent().id, home.id)
        self.assertFalse(TrashCan.objects.filter(page_id=page.id).exists())

    def test_restore_keeps_trash_like_text_in_original_slug(self):
        home = Page.objects.get(url_path="/home/")
        page = home.add_child(
            instance=Page(title="tips", slug="recycling-trash-5-tips")
        )
        trash_page(self.client, page)

        self.client.post(reverse("wagtail_trash_restore", args=(page.id,)))

        page.refresh_from_db()
        self.assertEqual(page.slug, "recycling-trash-5-tips")

    def test_restore_unknown_page_returns_404(self):
        response = self.client.post(reverse("wagtail_trash_restore", args=(999999,)))

        self.assertEqual(response.status_code, 404)

    def test_restore_and_move_unknown_page_returns_404(self):
        move_url = reverse("wagtail_trash_move", args=(999999,))
        home = Page.objects.get(url_path="/home/")

        self.assertEqual(self.client.get(move_url).status_code, 404)
        self.assertEqual(
            self.client.post(move_url, {"move_page": str(home.id)}).status_code, 404
        )

    def test_restore_and_move_already_restored_page_returns_404(self):
        home = Page.objects.get(url_path="/home/")
        page = home.add_child(instance=Page(title="page"))
        trash_page(self.client, page)
        self.client.post(reverse("wagtail_trash_restore", args=(page.id,)))
        move_url = reverse("wagtail_trash_move", args=(page.id,))

        self.assertEqual(self.client.get(move_url).status_code, 404)
        self.assertEqual(
            self.client.post(move_url, {"move_page": str(home.id)}).status_code, 404
        )
        self.assertEqual(Page.objects.get(id=page.id).get_parent().id, home.id)

    def test_restore_and_move_rejects_destination_disallowed_by_parent_page_types(self):
        home = Page.objects.get(url_path="/home/")
        section = home.add_child(instance=SectionPage(title="section"))
        article = section.add_child(instance=ArticlePage(title="article"))
        trash_page(self.client, article)

        response = self.client.post(
            reverse("wagtail_trash_move", args=(article.id,)),
            {"move_page": str(home.id)},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "move_page",
            "This page type is not allowed at the destination, choose another location.",
        )
        article.refresh_from_db()
        self.assertEqual(article.get_parent().specific_class, TrashCanPage)
        self.assertTrue(TrashCan.objects.filter(page_id=article.id).exists())

    def test_restore_and_move_allows_destination_permitted_by_parent_page_types(self):
        home = Page.objects.get(url_path="/home/")
        section = home.add_child(instance=SectionPage(title="section"))
        other_section = home.add_child(instance=SectionPage(title="other section"))
        article = section.add_child(instance=ArticlePage(title="article"))
        trash_page(self.client, article)

        self.client.post(
            reverse("wagtail_trash_move", args=(article.id,)),
            {"move_page": str(other_section.id)},
        )

        self.assertEqual(
            Page.objects.get(id=article.id).get_parent().id, other_section.id
        )
        self.assertFalse(TrashCan.objects.filter(page_id=article.id).exists())

    def test_restore_rejects_parent_that_reached_max_count_per_parent(self):
        home = Page.objects.get(url_path="/home/")
        singleton = home.add_child(
            instance=SingletonPage(title="singleton", slug="one")
        )
        trash_page(self.client, singleton)
        home.add_child(instance=SingletonPage(title="replacement", slug="two"))

        response = self.client.post(
            reverse("wagtail_trash_restore", args=(singleton.id,))
        )

        self.assertRedirects(
            response,
            reverse("wagtail_trash_move", args=(singleton.id,)),
            fetch_redirect_response=False,
        )
        self.assertEqual(
            [m.level_tag for m in get_messages(response.wsgi_request)][-1], "error"
        )
        singleton.refresh_from_db()
        self.assertEqual(singleton.get_parent().specific_class, TrashCanPage)
        self.assertTrue(TrashCan.objects.filter(page_id=singleton.id).exists())

    def test_delete_get_shows_confirmation_without_trashing(self):
        home = Page.objects.get(url_path="/home/")
        page = home.add_child(instance=Page(title="page"))

        response = self.client.get(
            reverse("wagtailadmin_pages:delete", args=(page.id,))
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Page.objects.get(id=page.id).get_parent().id, home.id)
        self.assertFalse(TrashCan.objects.exists())

    def test_deleting_page_in_trash_deletes_it_permanently(self):
        home = Page.objects.get(url_path="/home/")
        page = home.add_child(instance=Page(title="page"))
        child = page.add_child(instance=Page(title="child"))
        delete_url = reverse("wagtailadmin_pages:delete", args=(page.id,))
        self.client.post(delete_url)

        self.client.post(delete_url)

        self.assertFalse(Page.objects.filter(id__in=[page.id, child.id]).exists())
        self.assertFalse(TrashCan.objects.exists())

    def test_bulk_deleting_page_in_trash_deletes_it_permanently(self):
        home = Page.objects.get(url_path="/home/")
        page = home.add_child(instance=Page(title="page"))
        child = page.add_child(instance=Page(title="child"))
        bulk_delete_url = (
            reverse("wagtail_bulk_action", args=("wagtailcore", "page", "delete"))
            + f"?id={page.id}"
        )
        self.client.post(bulk_delete_url)
        self.assertTrue(TrashCan.objects.filter(page_id=page.id).exists())

        self.client.post(bulk_delete_url)

        self.assertFalse(Page.objects.filter(id__in=[page.id, child.id]).exists())
        self.assertFalse(TrashCan.objects.exists())

    def test_delete_redirects_to_next(self):
        home = Page.objects.get(url_path="/home/")
        page = home.add_child(instance=Page(title="page"))
        next_url = reverse("wagtailadmin_home")

        response = self.client.post(
            reverse("wagtailadmin_pages:delete", args=(page.id,)), {"next": next_url}
        )

        self.assertRedirects(response, next_url, fetch_redirect_response=False)

    def test_delete_ignores_external_next(self):
        home = Page.objects.get(url_path="/home/")
        page = home.add_child(instance=Page(title="page"))

        response = self.client.post(
            reverse("wagtailadmin_pages:delete", args=(page.id,)),
            {"next": "https://evil.example/"},
        )

        self.assertRedirects(
            response,
            reverse("wagtailadmin_explore", args=(home.id,)),
            fetch_redirect_response=False,
        )

    def test_bulk_delete_redirects_to_next(self):
        home = Page.objects.get(url_path="/home/")
        page = home.add_child(instance=Page(title="page"))
        next_url = reverse("wagtailadmin_home")

        response = self.client.post(
            reverse("wagtail_bulk_action", args=("wagtailcore", "page", "delete"))
            + f"?id={page.id}&next={next_url}"
        )

        self.assertRedirects(response, next_url, fetch_redirect_response=False)

    def test_bulk_delete_ignores_external_next(self):
        home = Page.objects.get(url_path="/home/")
        page = home.add_child(instance=Page(title="page"))

        response = self.client.post(
            reverse("wagtail_bulk_action", args=("wagtailcore", "page", "delete"))
            + f"?id={page.id}&next=https://evil.example/"
        )

        self.assertRedirects(
            response,
            reverse("wagtailadmin_explore", args=(home.id,)),
            fetch_redirect_response=False,
        )

    def test_trash_index_delete_get_shows_confirmation_without_deleting(self):
        home = Page.objects.get(url_path="/home/")
        page = home.add_child(instance=Page(title="page"))
        trash_page(self.client, page)
        rb = TrashCan.objects.get(page_id=page.id)

        response = self.client.get(
            trash_admin_url_helper.get_action_url("delete", rb.id)
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Page.objects.filter(id=page.id).exists())
        self.assertTrue(TrashCan.objects.filter(id=rb.id).exists())

    def test_trash_index_delete_removes_descendants(self):
        home = Page.objects.get(url_path="/home/")
        page = home.add_child(instance=Page(title="page"))
        child = page.add_child(instance=Page(title="child"))
        trash_page(self.client, page)
        rb = TrashCan.objects.get(page_id=page.id)

        self.client.post(trash_admin_url_helper.get_action_url("delete", rb.id))

        self.assertFalse(Page.objects.filter(id__in=[page.id, child.id]).exists())
        self.assertFalse(TrashCan.objects.exists())
