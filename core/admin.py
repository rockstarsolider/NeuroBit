# core/admin.py  – Django 5.2 • Unfold 0.24 • crispy-forms 2.x
from __future__ import annotations

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import (
    UserAdmin as DjangoUserAdmin,
    GroupAdmin as DjangoGroupAdmin,
)
from django.contrib.auth.forms import UserCreationForm, AdminPasswordChangeForm
from django.contrib.auth.models import Group
from django.db import models
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource

from unfold.admin import ModelAdmin
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.contrib.import_export.forms import ImportForm, ExportForm
from unfold.decorators import display
from unfold.contrib.forms.widgets import UnfoldAdminTextInputWidget

from .models import CustomUser
from . import notify as core_notify


# ──────────────────────────────────────────────────────
#  Widgets
# ──────────────────────────────────────────────────────
class UnfoldAdminPasswordInputWidget(UnfoldAdminTextInputWidget):
    """Password field with all Unfold CSS classes."""
    input_type = "password"


# ──────────────────────────────────────────────────────
#  Helpers for coloured badges
# ──────────────────────────────────────────────────────
def bool_badge(attr, *, true_text, false_text, true_color="success", false_color="danger"):
    @display(description=attr.replace("_", " ").title(), label={True: true_color, False: false_color})
    def badge(self, obj):
        val = getattr(obj, attr)
        return val, true_text if val else false_text
    badge.__name__ = f"{attr}_badge"
    return badge


def choice_badge(attr, mapping, *, description="Value"):
    label_map = {k: v[1] for k, v in mapping.items()}

    @display(description=description, label=label_map)
    def badge(self, obj):
        raw = getattr(obj, attr)
        text, _ = mapping.get(raw, (raw, "info"))
        return raw, text
    badge.__name__ = f"{attr}_badge"
    return badge


# ──────────────────────────────────────────────────────
#  Import-export resource
# ──────────────────────────────────────────────────────
class CustomUserResource(ModelResource):
    class Meta:
        model = CustomUser
        fields = (
            "id", "username", "first_name", "last_name", "birthdate",
            "email", "phone_number", "national_id",
            "is_active", "is_staff", "is_superuser", "date_joined",
        )
        export_order = fields


# ──────────────────────────────────────────────────────
#  Keep Group admin styled like Unfold
# ──────────────────────────────────────────────────────
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass


@admin.register(Group)
class GroupAdmin(DjangoGroupAdmin, ModelAdmin):
    pass


# ──────────────────────────────────────────────────────
#  Inline “add user” form (no external forms.py needed)
# ──────────────────────────────────────────────────────
class _AddUserForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            "username", "email", "phone_number", "birthdate", "national_id",
            "password1", "password2",
        )


# ──────────────────────────────────────────────────────
#  CustomUser admin
# ──────────────────────────────────────────────────────
@admin.register(CustomUser)
class CustomUserAdmin(DjangoUserAdmin, ModelAdmin, ImportExportModelAdmin):
    model = CustomUser

    # import-export
    resource_class = CustomUserResource
    import_form_class = ImportForm
    export_form_class = ExportForm

    # forms
    add_form = _AddUserForm
    change_password_form = AdminPasswordChangeForm

    # inject Unfold CSS for password widgets (add & change forms)
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        css = {"autocomplete": "new-password"}
        for name in ("password1", "password2", "password"):
            if name in form.base_fields:
                form.base_fields[name].widget = UnfoldAdminPasswordInputWidget(attrs=css)
        return form

    # list display helpers
    @display(description=_("Avatar"))
    def avatar(self, obj):
        if obj.image:
            return format_html('<img src="{}" class="rounded-full w-8 h-8">', obj.image.url)
        return "—"

    active_badge = bool_badge("is_active", true_text="YES", false_text="NO", true_color="success")
    staff_badge  = bool_badge("is_staff",  true_text="YES",  false_text="NO", true_color="success")
    super_badge  = bool_badge("is_superuser", true_text="YES", false_text="NO", true_color="success")
    gender_badge = choice_badge(
        "gender",
        mapping={"M": ("Male", "info"), "F": ("Female", "danger"), "O": ("Other", "secondary")},
        description=_("Gender"),
    )

    list_display = (
        "avatar", "first_name", "last_name", "username", "phone_number",
        "gender_badge",
        "staff_badge", "active_badge", "super_badge",
    )
    list_display_links = ["first_name", "last_name"]
    list_filter  = ("is_active", "is_staff", "is_superuser", "gender")
    search_fields = ("first_name", "last_name", "username", "email", "phone_number")
    ordering = ("username",)
    readonly_fields = ("last_login", "date_joined")

    # fieldsets (change form)
    fieldsets = (
        (None, {"fields": ("image", "username", "first_name", "last_name", "gender", "birthdate", "email", "phone_number", "national_id", "password")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    # add form layout
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "image",
                "username", "first_name", "last_name", "email", "phone_number", "birthdate",
                "password1", "password2",
            ),
        }),
    )

    # bulk actions
    @admin.action(description=_("Activate selected users"))
    def make_active(self, request, qs):
        qs.update(is_active=True)

    @admin.action(description=_("Deactivate selected users"))
    def make_inactive(self, request, qs):
        qs.update(is_active=False)

    actions = ("make_active", "make_inactive")

    # widgets
    formfield_overrides = {models.TextField: {"widget": WysiwygWidget}}


# ──────────────────────────────────────────────────────
#  SubscriptionNotificationConfig (singleton) — optimized
# ──────────────────────────────────────────────────────
@admin.register(core_notify.SubscriptionNotificationConfig)
class SubscriptionNotificationConfigAdmin(ModelAdmin):
    """
    Optimization: cache the 'exists()' check per request.
    Admin/Unfold may call has_add_permission() multiple times while building the UI;
    without caching, that results in duplicate `SELECT 1 FROM core_subscriptionnotificationconfig`.
    """
    list_display = ("enable_user_sms", "enable_manager_sms", "updated_at")
    formfield_overrides = {models.TextField: {"widget": WysiwygWidget}}

    fieldsets = ((None, {
        "fields": ("enable_user_sms", "enable_manager_sms", "manager_phones",
                   "user_sms_template", "manager_sms_template")
    }),)

    def get_queryset(self, request):
        # Only fetch what we show ⇒ smaller rows, better cache locality.
        qs = super().get_queryset(request)
        return qs.only("enable_user_sms", "enable_manager_sms", "updated_at")

    def has_add_permission(self, request):
        # Request-local cache to avoid duplicate EXISTS queries per page render.
        cached = getattr(request, "_cfg_sub_notif_exists", None)
        if cached is None:
            cached = core_notify.SubscriptionNotificationConfig.objects.only("id").exists()
            setattr(request, "_cfg_sub_notif_exists", cached)
        return not cached
