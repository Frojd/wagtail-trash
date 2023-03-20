from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.models import Page


class TrashCan(models.Model):
    page = models.ForeignKey(
        Page, on_delete=models.CASCADE, related_name="+", verbose_name=_("Page")
    )
    parent = models.ForeignKey(
        Page,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Parent"),
    )
    user = models.ForeignKey(
        get_user_model(), null=True, on_delete=models.SET_NULL, verbose_name=_("User")
    )
    time_recycled = models.DateTimeField(_("Time Recycled"), auto_now_add=True)
    data = models.TextField(_("Data"), blank=True)

    def __str__(self):
        return self.page.title

    class Meta:
        verbose_name = _("Trash Can")
        verbose_name_plural = _("Trash Cans")


class TrashCanPage(Page):
    parent_page_types = []
    subpage_types = []
