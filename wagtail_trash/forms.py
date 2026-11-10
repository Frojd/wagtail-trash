from django import forms
from django.utils.translation import gettext as _
from wagtail.admin.widgets import AdminPageChooser
from wagtail.models import Page


class MoveForm(forms.Form):
    move_page = forms.ModelChoiceField(
        queryset=Page.objects.all(),
        widget=AdminPageChooser(
            choose_one_text=_("Choose a root page"),
            choose_another_text=_("Choose a different root page"),
        ),
        error_messages={"invalid_choice": _("The chosen page does not exist.")},
    )
