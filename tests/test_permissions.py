from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.shortcuts import reverse
from django.test import TestCase
from wagtail.models import GroupPagePermission, Page
from wagtail.test.utils import WagtailTestUtils

from wagtail_trash.models import TrashCan
from wagtail_trash.wagtail_hooks import TrashCanModelAdmin

trash_admin_url_helper = TrashCanModelAdmin().url_helper


class TestPermissions(TestCase, WagtailTestUtils):
    def setUp(self):
        home = Page.objects.get(url_path="/home/")
        self.section = home.add_child(instance=Page(title="section"))
        self.other_section = home.add_child(instance=Page(title="other section"))

        self.superuser = self.create_superuser(username="admin", password="password")
        self.editor = self.create_editor(
            "editor", self.section, "add_page", "change_page", "publish_page"
        )
        self.drafter = self.create_editor(
            "drafter", self.section, "add_page", "change_page"
        )

    def create_editor(self, username, page, *page_permissions):
        user = get_user_model().objects.create_user(
            username=username, email=f"{username}@example.com", password="password"
        )
        group = Group.objects.create(name=username)
        group.permissions.add(
            Permission.objects.get(
                content_type__app_label="wagtailadmin", codename="access_admin"
            ),
            *Permission.objects.filter(content_type__app_label="wagtail_trash"),
        )
        for codename in page_permissions:
            GroupPagePermission.objects.create(
                group=group,
                page=page,
                permission=Permission.objects.get(
                    content_type__app_label="wagtailcore", codename=codename
                ),
            )
        user.groups.add(group)
        return user

    def trash(self, page, user):
        self.client.force_login(user)
        self.client.post(reverse("wagtailadmin_pages:delete", args=(page.id,)))
        self.assertTrue(TrashCan.objects.filter(page_id=page.id).exists())

    def assert_in_trash(self, page):
        self.assertTrue(TrashCan.objects.filter(page_id=page.id).exists())

    def assert_restored_under(self, page, parent):
        self.assertFalse(TrashCan.objects.filter(page_id=page.id).exists())
        self.assertEqual(Page.objects.get(id=page.id).get_parent().id, parent.id)

    def test_editor_can_view_trash_index(self):
        self.client.force_login(self.editor)

        response = self.client.get(trash_admin_url_helper.get_action_url("index"))

        self.assertEqual(response.status_code, 200)

    def test_editor_can_restore_page_in_own_section(self):
        page = self.section.add_child(instance=Page(title="page"))
        self.trash(page, self.editor)

        self.client.post(reverse("wagtail_trash_restore", args=(page.id,)))

        self.assert_restored_under(page, self.section)
        self.assertTrue(Page.objects.get(id=page.id).live)

    def test_editor_can_restore_and_move_within_own_section(self):
        page = self.section.add_child(instance=Page(title="page"))
        destination = self.section.add_child(instance=Page(title="destination"))
        self.trash(page, self.editor)

        self.client.post(
            reverse("wagtail_trash_move", args=(page.id,)),
            {"move_page": str(destination.id)},
        )

        self.assert_restored_under(page, destination)

    def test_editor_cannot_restore_page_from_other_section(self):
        page = self.other_section.add_child(instance=Page(title="page"))
        self.trash(page, self.superuser)

        self.client.force_login(self.editor)
        self.client.post(reverse("wagtail_trash_restore", args=(page.id,)))

        self.assert_in_trash(page)

    def test_editor_cannot_restore_and_move_into_other_section(self):
        page = self.section.add_child(instance=Page(title="page"))
        self.trash(page, self.editor)

        self.client.post(
            reverse("wagtail_trash_move", args=(page.id,)),
            {"move_page": str(self.other_section.id)},
        )

        self.assert_in_trash(page)

    def test_editor_without_publish_cannot_restore_live_page(self):
        page = self.section.add_child(instance=Page(title="page"))
        self.trash(page, self.superuser)

        self.client.force_login(self.drafter)
        self.client.post(reverse("wagtail_trash_restore", args=(page.id,)))

        self.assert_in_trash(page)

    def test_editor_without_publish_can_restore_draft_page(self):
        page = self.section.add_child(instance=Page(title="page", live=False))
        self.trash(page, self.drafter)

        self.client.post(reverse("wagtail_trash_restore", args=(page.id,)))

        self.assert_restored_under(page, self.section)
        self.assertFalse(Page.objects.get(id=page.id).live)
