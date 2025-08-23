from wagtail_trash.models import TrashCan


class SkipSitemapIfInTrashMixin:
    def get_sitemap_urls(self, request=None):
        if self.in_trash_can():
            return []

        return super().get_sitemap_urls(request=request)

    def in_trash_can(self) -> bool:
        return TrashCan.objects.filter(page=self).exists()
