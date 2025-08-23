from __future__ import annotations

from decimal import Decimal
from typing import List, Optional, Type

from django.contrib import admin, messages
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.contrib.humanize.templatetags.humanize import intcomma

from unfold.admin import ModelAdmin
from unfold.decorators import action
from unfold.enums import ActionVariant

from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields
from import_export.formats.base_formats import CSV, JSON, XLSX, Format

from django.conf import settings

from . import models as m


# ============
# Helper bits
# ============
def badge(text: str, variant: str) -> str:
    # Unfold badges
    # Variants: primary, success, info, warning, danger, default
    return f'<span class="badge badge--{variant}">{text}</span>'


def _format_shamsi(dt) -> str:
    # Prefer model helpers if present.
    if hasattr(dt, "strftime"):
        # Fallback Gregorian readable
        return timezone.localtime(dt).strftime("%Y-%m-%d %H:%M")
    return "—"


# ===============================
# Import/Export resource (clean!)
# ===============================
class LearnerSubscribePlanResource(resources.ModelResource):
    learner = fields.Field(column_name="learner_full_name")
    plan = fields.Field(column_name="plan_name")
    start = fields.Field(attribute="start_datetime", column_name="start_datetime")
    end = fields.Field(attribute="end_datetime", column_name="end_datetime")
    discount = fields.Field(attribute="discount", column_name="discount_percent")
    final_cost = fields.Field(attribute="final_cost", column_name="final_cost_toman")
    status = fields.Field(attribute="status", column_name="status")

    class Meta:
        model = m.LearnerSubscribePlan
        fields = (
            "learner",
            "plan",
            "start",
            "end",
            "discount",
            "final_cost",
            "status",
        )
        export_order = (
            "learner",
            "plan",
            "start",
            "end",
            "discount",
            "final_cost",
            "status",
        )

    # Computed fields
    def dehydrate_learner(self, obj: m.LearnerSubscribePlan) -> str:
        try:
            u = obj.learner_enrolment.learner.user
            return f"{u.first_name} {u.last_name}".strip() or u.email
        except Exception:
            return str(obj.learner_enrolment_id)

    def dehydrate_plan(self, obj: m.LearnerSubscribePlan) -> str:
        return getattr(obj.subscription_plan, "name", str(obj.subscription_plan_id))


# -----------------------------------------
# Optional PDF format (guarded & graceful)
# -----------------------------------------
class PDF(Format):
    def get_title(self):       return "pdf"
    def get_extension(self):   return "pdf"
    def get_content_type(self):return "application/pdf"

    def export_data(self, dataset, **kwargs):
        html = render_to_string(
            "admin/courses/learner_subscribe_plan/export_pdf.html",
            {"dataset": dataset, "generated_at": timezone.now()},
        )
        if getattr(settings, "USE_WEASYPRINT", False):
            try:
                from weasyprint import HTML
                return HTML(string=html).write_pdf()
            except Exception as exc:
                # Fall back to HTML bytes if WeasyPrint missing/broken
                # (and show a warning in the admin flash messages if we have a request in context)
                pass
        return html.encode("utf-8")


# ===========================================
# Inline: show transactions under a sub plan
# ===========================================
class TransactionInline(admin.TabularInline):
    model = m.SubscriptionTransaction
    extra = 0
    fields = ("paid_at", "kind", "status", "amount", "gateway", "ref", "note")
    readonly_fields = ("paid_at", "kind", "status", "amount", "gateway", "ref")


# =====================================
# Main admin for LearnerSubscribePlan
# =====================================
@admin.register(m.LearnerSubscribePlan)
class LearnerSubscribePlanAdmin(ModelAdmin, ImportExportModelAdmin):
    # Unfold + Import/Export integration
    import_form_class = None  # Unfold's ImportForm can be set if you use imports
    from unfold.contrib.import_export.forms import ExportForm  # styled
    export_form_class = ExportForm
    resource_classes = [LearnerSubscribePlanResource]

    # Inline
    inlines = (TransactionInline,)

    # Query perf
    list_select_related = (
        "learner_enrolment__learner__user",
        "learner_enrolment__learning_path",
        "subscription_plan",
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            "learner_enrolment__learner__user",
            "learner_enrolment__learning_path",
            "subscription_plan",
        )

    # Changelist columns (no ID!)
    list_display = (
        "learner_full_name",
        "plan_name",
        "start_shamsi",
        "end_shamsi",
        "discount_percent",
        "final_cost_h",
        "status_badge",
    )
    list_filter = ("status", "subscription_plan")
    search_fields = (
        "learner_enrolment__learner__user__first_name",
        "learner_enrolment__learner__user__last_name",
        "subscription_plan__name",
    )
    ordering = ("-start_datetime", "-id")
    list_per_page = 50
    readonly_fields = ("end_datetime", "final_cost", "expired_at")

    # Clean action button (visible on listing top)
    actions_list = ["go_analytics_dropdown"]

    @action(
        description=_("Analytics & Export"),
        icon="query_stats",
        variant=ActionVariant.PRIMARY,
    )
    def go_analytics_dropdown(self, request: HttpRequest, queryset):
        # Send users to analytics (no queryset use)
        return self._redirect_to_analytics(request)

    def _redirect_to_analytics(self, request: HttpRequest):
        return admin.redirects.redirect(reverse("admin:courses_learnersubscribeplan_analytics"))

    # Pretty accessors
    def learner_full_name(self, obj: m.LearnerSubscribePlan) -> str:
        u = obj.learner_enrolment.learner.user
        return f"{u.first_name} {u.last_name}".strip() or u.email

    def plan_name(self, obj: m.LearnerSubscribePlan) -> str:
        return obj.subscription_plan.name

    def start_shamsi(self, obj: m.LearnerSubscribePlan) -> str:
        if hasattr(obj, "start_shamsi"):
            return obj.start_shamsi
        return _format_shamsi(obj.start_datetime)

    def end_shamsi(self, obj: m.LearnerSubscribePlan) -> str:
        if hasattr(obj, "end_shamsi"):
            return obj.end_shamsi
        return _format_shamsi(obj.end_datetime)

    def discount_percent(self, obj: m.LearnerSubscribePlan) -> str:
        try:
            return f"{int(Decimal(obj.discount))}%"
        except Exception:
            return f"{obj.discount}%"

    def final_cost_h(self, obj: m.LearnerSubscribePlan) -> str:
        return f"{intcomma(obj.final_cost)}"

    def status_badge(self, obj: m.LearnerSubscribePlan) -> str:
        if obj.status == m.LearnerSubscribePlan.STATUS_ACTIVE:
            return format_html(badge(_("Active"), "success"))
        elif obj.status == m.LearnerSubscribePlan.STATUS_EXPIRED:
            return format_html(badge(_("Expired"), "danger"))
        return format_html(badge(str(obj.status), "default"))

    status_badge.short_description = _("Status")
    learner_full_name.short_description = _("Learner")
    plan_name.short_description = _("Plan")
    start_shamsi.short_description = _("Start (Shamsi)")
    end_shamsi.short_description = _("End (Shamsi)")
    discount_percent.short_description = _("Disc")
    final_cost_h.short_description = _("Final Cost")

    # ====== Export formats (FIXES your error) ======
    def get_export_formats(self) -> List[Type[Format]]:
        """
        MUST return a list of **classes**, not instances.
        """
        fmts: List[Type[Format]] = [CSV, JSON, XLSX]  # Excel via XLSX
        # Only offer PDF when explicitly enabled (and template exists).
        if getattr(settings, "USE_WEASYPRINT", False):
            fmts.append(PDF)
        return fmts

    # ====== URLs for analytics and JSON data ======
    def get_urls(self):
        return [
            path(
                "analytics/",
                self.admin_site.admin_view(self.analytics_view),
                name="courses_learnersubscribeplan_analytics",
            ),
            path(
                "analytics/data/",
                self.admin_site.admin_view(self.analytics_data),
                name="courses_learnersubscribeplan_analytics_data",
            ),
        ] + super().get_urls()

    def analytics_view(self, request: HttpRequest):
        ctx = dict(
            self.admin_site.each_context(request),
            title=_("Subscriptions Analytics"),
        )
        # Template path you already have in your repo
        return TemplateResponse(
            request,
            "admin/courses/learnersubscribeplan/analytics.html",
            ctx,
        )

    def analytics_data(self, request: HttpRequest):
        """
        JSON API used by your front-end (Chart.js / Plotly).

        Query params:
          - chart: monthly_revenue | plan_counts | paths_pie | age_scatter
          - year:  YYYY (default: current year)
          - month: 1..12 (optional for plan_counts)
          - scope: 'active' or 'all' (default: all)
        """
        chart = request.GET.get("chart") or "monthly_revenue"
        year = int(request.GET.get("year") or timezone.now().year)
        month = request.GET.get("month")
        scope = (request.GET.get("scope") or "all").lower()

        qs = m.LearnerSubscribePlan.objects.select_related(
            "subscription_plan",
            "learner_enrolment__learner__user",
            "learner_enrolment__learning_path",
        )
        if scope == "active":
            qs = qs.filter(status=m.LearnerSubscribePlan.STATUS_ACTIVE)

        # --- Monthly revenue / count ---
        if chart == "monthly_revenue":
            rows = (
                qs.filter(start_datetime__year=year)
                .annotate(m=TruncMonth("start_datetime"))
                .values("m")
                .order_by("m")
                .annotate(revenue=Sum("final_cost"), count=Count("id"))
            )
            labels, revenues, counts = [], [], []
            for r in rows:
                mval = r["m"]
                labels.append(mval.strftime("%Y-%m"))
                revenues.append(int(r["revenue"] or 0))
                counts.append(int(r["count"] or 0))
            return JsonResponse(
                {"chart": chart, "year": year, "labels": labels, "revenues": revenues, "counts": counts}
            )

        # --- Plan counts for a specific month/year ---
        if chart == "plan_counts":
            if month:
                m_int = int(month)
                rows = (
                    qs.filter(start_datetime__year=year, start_datetime__month=m_int)
                    .values("subscription_plan__name")
                    .annotate(c=Count("id"))
                    .order_by("-c")
                )
            else:
                rows = (
                    qs.filter(start_datetime__year=year)
                    .values("subscription_plan__name")
                    .annotate(c=Count("id"))
                    .order_by("-c")
                )
            labels = [r["subscription_plan__name"] or "—" for r in rows]
            counts = [int(r["c"] or 0) for r in rows]
            return JsonResponse(
                {
                    "chart": chart,
                    "year": year,
                    "month": int(month) if month else None,
                    "labels": labels,
                    "counts": counts,
                    "total": sum(counts),
                }
            )

        # --- Learners per learning-path (Pie) ---
        if chart == "paths_pie":
            try:
                rows = (
                    qs.filter(start_datetime__year=year)
                    .values("learner_enrolment__learning_path__name")
                    .annotate(c=Count("id"))
                    .order_by("-c")
                )
                labels = [r["learner_enrolment__learning_path__name"] or "—" for r in rows]
                values = [int(r["c"] or 0) for r in rows]
            except Exception:
                labels, values = [], []
            return JsonResponse({"chart": chart, "labels": labels, "values": values})

        # --- Age vs revenue (Scatter) ---
        if chart == "age_scatter":
            # Aggregate revenue per learner for selected year
            rev = (
                qs.filter(start_datetime__year=year)
                .values("learner_enrolment__learner_id")
                .annotate(total=Sum("final_cost"))
            )
            rev_map = {r["learner_enrolment__learner_id"]: int(r["total"] or 0) for r in rev if r["learner_enrolment__learner_id"]}
            learner_ids = list(rev_map.keys())

            ages, totals = [], []
            if learner_ids:
                # DOB is on CustomUser (you told me that)
                from core.models import CustomUser
                users = (
                    CustomUser.objects.filter(learner__id__in=learner_ids)
                    .only("id", "date_of_birth")
                )
                today = timezone.now().date()
                # Map learner_id -> age
                # Need learner_id -> user map
                # learner -> user is 1-1 through Learner model
                learners = m.Learner.objects.filter(id__in=learner_ids).select_related("user")
                for lr in learners:
                    dob = getattr(lr.user, "date_of_birth", None)
                    if dob:
                        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                        if 5 <= age <= 100:
                            ages.append(int(age))
                            totals.append(rev_map.get(lr.id, 0))

            return JsonResponse({"chart": chart, "x": ages, "y": totals, "x_title": "Age", "y_title": "Revenue (T)"})

        # default
        return JsonResponse({"chart": chart, "labels": [], "revenues": [], "counts": []})
