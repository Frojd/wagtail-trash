from django.test import TestCase


class TestPages(TestCase):
    def test_delete_page_moves_to_bin(self):
        # Delete page

        # Page still exists

        # Page is under bin
        pass

    def test_delete_page_unpublishes_pages(self):
        # Delete page

        # Page still exists

        # Page is under bin
        pass

    def test_undelete_moves_page_back_where_it_belongs_if_possible(self):
        # Undelete page

        # Page is where it previously was
        pass

    def test_undelete_errors_if_source_page_is_removed(self):
        # Create a section
        # Create a page under section
        # Delete page
        # Delete section

        # Undelete page doesn't work since section is in bin

        # Delete section from bin

        # Undelete page doesn't work since section doesn't exist
        pass

    def test_move_from_bin_resets_published_pages(self):
        # Delete page with some published/unpublished pages

        # Undelete page, all published pages is back to normal, unpublished unchanged
        pass
