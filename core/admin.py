# core/admin.py – Django 5.2 • Unfold 0.24 • django‑import‑export 4.x
from __future__ import annotations

from django import forms
from django.contrib import admin
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
from django.db import models
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource

from unfold.admin import ModelAdmin
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.contrib.import_export.forms import ExportForm, ImportForm
from unfold.decorators import display

from .models import CustomUser


# ────────────────────────────────────────────────────────────────
#  Helpers (same pattern as courses.admin)
# ────────────────────────────────────────────────────────────────
def bool_badge(
    attr: str,
    *,
    true_text="Yes",
    false_text="No",
    true_color="success",
    false_color="danger",
    description="Status",
):
    @display(description=description, label={True: true_color, False: false_color})
    def _method(self, obj):
        raw = getattr(obj, attr)
        return raw, true_text if raw else false_text

    _method.__name__ = f"{attr}_badge"
    return _method


def choice_badge(attr: str, *, mapping: dict[str, tuple[str, str]], description="Value"):
    label_map = {k: v[1] for k, v in mapping.items()}

    @display(description=description, label=label_map)
    def _method(self, obj):
        raw = getattr(obj, attr)
        text, _ = mapping.get(raw, (raw, "info"))
        return raw, text

    _method.__name__ = f"{attr}_badge"
    return _method


# ────────────────────────────────────────────────────────────────
#  Import‑Export resource
# ────────────────────────────────────────────────────────────────
class CustomUserResource(ModelResource):
    class Meta:
        model = CustomUser
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "city",
            "gender",
            "is_active",
            "is_staff",
            "is_superuser",
            "date_joined",
        )
        export_order = fields


# ────────────────────────────────────────────────────────────────
#  Unfold‑styled Group admin
# ────────────────────────────────────────────────────────────────
admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    """Pure styling pass‑through for the built‑in Group table."""


# ────────────────────────────────────────────────────────────────
#  Custom forms (Unfold + extra fields)
# ────────────────────────────────────────────────────────────────
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "image",
            "password1",
            "password2",
        )


class CustomUserChangeForm(UserChangeForm):
    home_number = forms.CharField(
        label=_("Home phone"),
        required=False,
        widget=forms.TextInput(attrs={"placeholder": _("e.g. +49 123 456")}),
    )

    class Meta(UserChangeForm.Meta):
        model = CustomUser
        widgets = {models.TextField: {"widget": WysiwygWidget}}
        fields = "__all__"


# ────────────────────────────────────────────────────────────────
#  Main admin
# ────────────────────────────────────────────────────────────────
@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin, ModelAdmin, ImportExportModelAdmin):
    # Import‑Export glue
    resource_class = CustomUserResource
    import_form_class = ImportForm
    export_form_class = ExportForm
    show_full_result_count = False

    # Forms
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    change_password_form = AdminPasswordChangeForm
    model = CustomUser

    # — Badge helpers —
    active_badge = bool_badge(
        "is_active",
        true_text="Active",
        false_text="Inactive",
        true_color="success",
        false_color="danger",
        description=_("Active"),
    )
    staff_badge = bool_badge(
        "is_staff",
        true_text="Staff",
        false_text="No",
        true_color="primary",
        false_color="secondary",
        description=_("Staff"),
    )
    superuser_badge = bool_badge(
        "is_superuser",
        true_text="Superuser",
        false_text="No",
        true_color="warning",
        false_color="secondary",
        description=_("Superuser"),
    )
    gender_badge = choice_badge(
        "gender",
        mapping={
            "M": ("Male", "info"),
            "F": ("Female", "danger"),
            "O": ("Other", "secondary"),
        },
        description=_("Gender"),
    )

    # — List page —
    @display(description=_("Avatar"))
    def avatar_thumb(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:32px;height:32px;border-radius:50%" />',
                obj.image.url,
            )
        return "—"

    list_display = (
        "avatar_thumb",
        "username",
        "email",
        "phone_number",
        "city",
        "gender_badge",
        "staff_badge",
        "active_badge",
        "superuser_badge",
    )
    list_display_links = ("username",)
    list_filter = ("is_active", "is_staff", "is_superuser", "gender", "city")
    search_fields = ("username", "first_name", "last_name", "email", "phone_number")
    ordering = ("username",)

    # — Form layout —
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "username",
                    ("first_name", "last_name"),
                    ("email", "phone_number"),
                    "image",
                    ("gender", "birthdate"),
                    "city",
                    ("national_id", "home_number"),
                    "password",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_staff",
                    "is_active",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "phone_number",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )

    readonly_fields = ("last_login", "date_joined")

    # — Bulk actions —
    @admin.action(description="Activate selected users")
    def make_active(self, request, qs):
        qs.update(is_active=True)

    @admin.action(description="Deactivate selected users")
    def make_inactive(self, request, qs):
        qs.update(is_active=False)

    actions = ("make_active", "make_inactive")
