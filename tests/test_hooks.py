from django.test import TestCase


class TestHooks(TestCase):
    def test_page_chooser_queryset(self):
        # Number of pages is 2

        # Add a trashcan

        # Number of pages is still 2
        pass

    def test_construct_explorer_page_queryset(self):
        # Number of pages is 2

        # Add a trashcan

        # Number of pages is still 2
        pass

    def test_delete_page_triggers_hook(self):
        pass

    def test_move_page_triggers_hook(self):
        pass
