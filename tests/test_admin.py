from django.test import TestCase
from wagtail.tests.utils import WagtailTestUtils
from wagtail_recycle_bin.models import RecycleBinPage
from wagtail_recycle_bin.wagtail_hooks import RecycleBinModelAdmin

recycle_admin_url_helper = RecycleBinModelAdmin().url_helper


class TestHooks(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

    def test_visiting_bin_creates_one_if_not_exists(self):
        index_url = recycle_admin_url_helper.get_action_url("index")

        assert RecycleBinPage.objects.count() == 0

        resp = self.client.get(index_url)

        assert RecycleBinPage.objects.count() == 1

        self.client.get(index_url)

        assert RecycleBinPage.objects.count() == 1
