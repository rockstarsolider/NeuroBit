# core/admin.py ― Django 5.2 + Unfold 0.24
from __future__ import annotations

from django import forms
from django.contrib import admin
from django.db import models
from django.contrib.auth.admin import (
    UserAdmin as BaseUserAdmin,
    GroupAdmin as BaseGroupAdmin,
)
from django.contrib.auth.forms import (
    AdminPasswordChangeForm,
    UserChangeForm,
    UserCreationForm,
)
from django.contrib.auth.models import Group
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from unfold.admin import ModelAdmin
from unfold.decorators import display
from unfold.contrib.forms.widgets import WysiwygWidget

from .models import CustomUser


# ────────────────────────────────────────────────────────────────
#  Unregister → re‑register Group with Unfold styling
# ────────────────────────────────────────────────────────────────
admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    """Nothing fancy—just lets Unfold style the built‑in groups table."""


# ────────────────────────────────────────────────────────────────
#  Custom forms (keep Unfold defaults but add the image field)
# ────────────────────────────────────────────────────────────────
class CustomUserCreationForm(UserCreationForm):
    """Expose image + phone in the add popup."""
    class Meta(UserCreationForm.Meta):
        model  = CustomUser
        fields = (
            "username", "first_name", "last_name", "email",
            "phone_number", "image", "password1", "password2",
        )


class CustomUserChangeForm(UserChangeForm):
    """Expose extra fields & rich‑text widget for home_number if desired."""
    home_number = forms.CharField(
        label=_("Home phone"),
        required=False,
        widget=forms.TextInput(attrs={"placeholder": _("e.g. +49 123 456")}),
    )

    class Meta(UserChangeForm.Meta):
        model  = CustomUser
        widgets = {models.TextField: {"widget": WysiwygWidget}}
        fields = "__all__"


# ────────────────────────────────────────────────────────────────
#  Main admin class
# ────────────────────────────────────────────────────────────────
@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin, ModelAdmin):
    """
    A sleek Unfold admin for CustomUser.
    We keep the classic username login but surface phone, avatar, and profile info.
    """
    form                 = CustomUserChangeForm
    add_form             = CustomUserCreationForm
    change_password_form = AdminPasswordChangeForm
    model                = CustomUser

    # — List page —
    @display(description=_("Avatar"))
    def avatar_thumb(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:32px;height:32px;border-radius:50%" />',
                obj.image.url,
            )
        return "—"

    list_display  = (
        "avatar_thumb", "username", "email",
        "phone_number", "city",
        "is_staff", "is_active", "is_superuser",
    )
    list_display_links = ("username",)
    list_filter   = ("is_staff", "is_active", "is_superuser", "gender", "city")
    search_fields = ("username", "first_name", "last_name", "email", "phone_number")
    ordering      = ("username",)

    # — Detail form layout —
    fieldsets = (
        (None, {
            "fields": (
                "username", ("first_name", "last_name"),
                ("email", "phone_number"), "image",
                ("gender", "birthdate"), "city",
                ("national_id", "home_number"),
                "password",
            )
        }),
        (_("Permissions"), {
            "fields": (
                "is_staff", "is_active", "is_superuser",
                "groups", "user_permissions",
            )
        }),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    # — Add‑user popup —
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username", "email", "phone_number",
                "password1", "password2",
                "is_staff", "is_active",
            ),
        }),
    )

    # — Read‑only dates —
    readonly_fields = ("last_login", "date_joined")
