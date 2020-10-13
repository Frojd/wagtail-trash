from django.test import TestCase
from django.shortcuts import reverse
from wagtail.tests.utils import WagtailTestUtils
from wagtail.core.models import Page
from wagtail_recycle_bin.views import recycle_delete
from wagtail_recycle_bin.models import RecycleBinPage
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
        root_page = Page.objects.get(url_path='/')

        new_page = Page(title='new page')
        root_page.add_child(instance=new_page)


        with self.register_hook('before_delete_page', recycle_delete):
            delete_url = (
                reverse('wagtailadmin_pages:delete', args=(new_page.id,))
            )
            self.client.post(delete_url)

        new_page = Page.objects.filter(title='new page')

        assert new_page.exists()

        assert new_page.child_of(RecycleBinPage.objects.first())

    def test_removing_page_from_bin_deletes_it(self):
        root_page = Page.objects.get(url_path='/')

        new_page = Page(title='delete page')
        root_page.add_child(instance=new_page)

        with self.register_hook('before_delete_page', recycle_delete):
            delete_url = (
                reverse('wagtailadmin_pages:delete', args=(new_page.id,))
            )
            self.client.post(delete_url)

            delete_url = (
                reverse('wagtailadmin_pages:delete', args=(new_page.id,))
            )
            self.client.post(delete_url)

        assert not Page.objects.filter(title='delete page')
