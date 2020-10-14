from django import forms
from django.utils.translation import gettext as _
from wagtail.admin.widgets import AdminPageChooser


class MoveForm(forms.Form):
    move_page = forms.CharField(
        widget=AdminPageChooser(
            choose_one_text=_("Choose a root page"),
            choose_another_text=_("Choose a different root page"),
        )
    )
