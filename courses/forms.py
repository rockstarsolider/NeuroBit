from django import forms
from core.models import CustomUser
from courses.models import Mentor
from django.utils.translation import gettext_lazy as _

class ProfileForm(forms.ModelForm):
    hire_date = forms.DateField(required=False, label=_("Hire Date"),
        widget=forms.DateInput(attrs={
            "type": "date", "readonly": True,
            "class": "mt-1 block w-full rounded-md border-gray-300 shadow-sm bg-gray-100 cursor-not-allowed "
                     "focus:border-[var(--primary-color)] focus:ring-[var(--primary-color)] sm:text-sm h-12 px-4"
        })
    )
    address = forms.CharField(required=False, label=_("Address"),
        widget=forms.TextInput(attrs={
            "class": "mt-1 block w-full rounded-md border-gray-300 shadow-sm "
                     "focus:border-[var(--primary-color)] focus:ring-[var(--primary-color)] sm:text-sm h-12 px-4"
        })
    )
    bio = forms.CharField(required=False, label=_("Bio"),
        widget=forms.Textarea(attrs={
            "class": "mt-1 block w-full rounded-md border-gray-300 shadow-sm "
                     "focus:border-[var(--primary-color)] focus:ring-[var(--primary-color)] sm:text-sm p-4",
            "rows": "4"
        })
    )
    specialties = forms.ModelMultipleChoiceField(required=False, label=_("Specialties"),
        queryset=Mentor._meta.get_field("specialties").remote_field.model.objects.all(),
        widget=forms.SelectMultiple(attrs={
            "class": "mt-1 block w-full rounded-md border-gray-300 shadow-sm "
                     "focus:border-[var(--primary-color)] focus:ring-[var(--primary-color)] sm:text-sm p-2"
        })
    )
    mother_phone = forms.CharField(required=False, label=_("Mother phone number"),
        widget=forms.TextInput(attrs={"class": "mt-1 block w-full rounded-md border-gray-300 shadow-sm "
                                      "focus:border-[var(--primary-color)] focus:ring-[var(--primary-color)] sm:text-sm h-12 px-4",
                                      "placeholder": _("Mother's phone number")}))
    father_phone = forms.CharField(required=False, label=_("Father phone number"),
        widget=forms.TextInput(attrs={"class": "mt-1 block w-full rounded-md border-gray-300 shadow-sm "
                                      "focus:border-[var(--primary-color)] focus:ring-[var(--primary-color)] sm:text-sm h-12 px-4",
                                      "placeholder": _("Father's phone number")}))

    class Meta:
        model = CustomUser
        fields = ["username", "first_name", "last_name", "email", "birthdate", "image"]
        labels = {f: _(f.replace("_", " ").title()) for f in fields}
        widgets = {
            "username": forms.TextInput(attrs={"class": "mt-1 block w-full rounded-md border-gray-300 shadow-sm "
                                                "focus:border-[var(--primary-color)] focus:ring-[var(--primary-color)] "
                                                "sm:text-sm h-12 px-4",}),
            "first_name": forms.TextInput(attrs={"class": "mt-1 block w-full rounded-md border-gray-300 shadow-sm "
                                                 "focus:border-[var(--primary-color)] focus:ring-[var(--primary-color)] sm:text-sm h-12 px-4"}),
            "last_name": forms.TextInput(attrs={"class": "mt-1 block w-full rounded-md border-gray-300 shadow-sm "
                                                "focus:border-[var(--primary-color)] focus:ring-[var(--primary-color)] sm:text-sm h-12 px-4"}),
            "email": forms.EmailInput(attrs={"class": "mt-1 block w-full rounded-md border-gray-300 shadow-sm "
                                             "focus:border-[var(--primary-color)] focus:ring-[var(--primary-color)] sm:text-sm h-12 px-4"}),
            "birthdate": forms.DateInput(attrs={"type": "date",
                                               "class": "mt-1 block w-full rounded-md border-gray-300 shadow-sm "
                                                        "focus:border-[var(--primary-color)] focus:ring-[var(--primary-color)] sm:text-sm h-12 px-4"}),
            "image": forms.FileInput(attrs={"class": "rounded-md border bg-(--primary-color) border-gray-300 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-blue-600 cursor-pointer focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-(--primary-color)"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.get("instance")
        super().__init__(*args, **kwargs)

        # Mentor fields
        if hasattr(user, "mentor_profile"):
            m = user.mentor_profile
            for f in ["hire_date", "address", "bio"]:
                self.fields[f].initial = getattr(m, f)
                self.fields[f].widget.attrs["placeholder"] = getattr(m, f) or self.fields[f].label
            self.fields["specialties"].initial = m.specialties.all()
            self.fields["specialties"].widget.attrs["data-placeholder"] = ", ".join(s.name for s in m.specialties.all()) if m.specialties.exists() else "Select specialties"
        else:
            for f in ["hire_date", "address", "bio", "specialties"]:
                self.fields.pop(f, None)

        # Learner fields
        if hasattr(user, "learner_profile"):
            l = user.learner_profile
            for f in ["mother_phone", "father_phone"]:
                self.fields[f].initial = getattr(l, f)
                self.fields[f].widget.attrs["placeholder"] = getattr(l, f) or self.fields[f].label
        else:
            for f in ["mother_phone", "father_phone"]:
                self.fields.pop(f, None)

    def save(self, commit=True):
        user = super().save(commit)
        if hasattr(user, "mentor_profile"):
            m = user.mentor_profile
            m.hire_date = self.cleaned_data.get("hire_date")
            m.address = self.cleaned_data.get("address")
            m.bio = self.cleaned_data.get("bio")
            m.specialties.set(self.cleaned_data.get("specialties"))
            if commit: m.save()
        if hasattr(user, "learner_profile"):
            l = user.learner_profile
            l.mother_phone = self.cleaned_data.get("mother_phone")
            l.father_phone = self.cleaned_data.get("father_phone")
            if commit: l.save()
        return user