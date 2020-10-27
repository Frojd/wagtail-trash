from django.test import TestCase
from django.shortcuts import reverse
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from wagtail.core.models import GroupPagePermission
from wagtail.tests.utils import WagtailTestUtils
from wagtail.core.models import Page
from wagtail_recycle_bin.views import recycle_delete
from wagtail_recycle_bin.models import RecycleBinPage, RecycleBin
from wagtail_recycle_bin.wagtail_hooks import RecycleBinModelAdmin

recycle_admin_url_helper = RecycleBinModelAdmin().url_helper


class TestPermissions(TestCase, WagtailTestUtils):
    pass
    # def setUp(self):
    #     self.group = Group.objects.create(name="Wowie Kazowie")
    #     moderators = Group.objects.filter(name="Moderators").first()

    #     self.test_user_with_permission = get_user_model().objects.create_user(
    #         username="wowie",
    #         email="kazowie@wowoie.test",
    #         password="password123",
    #         first_name="Wowie",
    #         last_name="Kazowie",
    #     )

    #     self.test_user_without_permission = get_user_model().objects.create_user(
    #         username="not_worthy",
    #         email="not@worthy.test",
    #         password="hunter2",
    #         first_name="Not",
    #         last_name="Worthy",
    #     )

    #     admin_permission = Permission.objects.get(content_type__app_label='wagtailadmin', codename='access_admin')
    #     recycle_permissions = Permission.objects.filter(content_type__app_label__startswith='wagtail_recycle_bin')


    #     self.test_user_with_permission.groups.add(self.group, moderators)
    #     self.test_user_with_permission.user_permissions.add(admin_permission, *recycle_permissions)
    #     self.test_user_without_permission.groups.add(moderators)
    #     self.test_user_without_permission.user_permissions.add(admin_permission, *recycle_permissions)

    #     self.root_page = Page.objects.get(url_path="/")

    #     self.top_page = Page(title="top_page")
    #     self.root_page.add_child(instance=self.top_page)

    #     self.sub_page = Page(title="top_page")
    #     self.top_page.add_child(instance=self.sub_page)

    #     self.group_permission = GroupPagePermission.objects.create(
    #         page=self.top_page, permission_type="edit", group=self.group
    #     )

    # def login_permissions(self):
    #     self.client.login(username="wowie", password="password123")

    # def login_no_permissions(self):
    #     self.client.login(username="not_worthy", password="hunter2")

    # def test_permissions(self):
    #     index_url = recycle_admin_url_helper.get_action_url("index")

    #     self.login_permissions()

    #     resp = self.client.get(index_url)
    #     html = str(resp.content)


    #     self.assertEquals(html.count("data-object-pk"), 0)

    #     with self.register_hook("before_delete_page", recycle_delete):
    #         delete_url = reverse("wagtailadmin_pages:delete", args=(self.top_page.id,))
    #         self.client.post(delete_url)

    #     resp = self.client.get(index_url)
    #     html = str(resp.content)
    #     print(html)

    #     self.assertEquals(html.count("data-object-pk"), 1)
