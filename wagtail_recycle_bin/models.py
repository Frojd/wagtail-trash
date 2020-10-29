from django.db import models
from django.contrib.auth import get_user_model
from wagtail.core.models import Page


class TrashCan(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="+")
    parent = models.ForeignKey(
        Page, null=True, on_delete=models.SET_NULL, related_name="+"
    )
    user = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL)
    time_recycled = models.DateTimeField(auto_now_add=True)
    data = models.TextField(blank=True)

    def __str__(self):
        return self.page.title


class TrashCanPage(Page):
    parent_page_types = []
    subpage_types = []
