from datetime import date
from django import forms
from core.models import *
from django.utils import timezone
from django.contrib.auth import get_user_model
from phonenumber_field.formfields import PhoneNumberField

User = get_user_model()

Schedule_TYPE = (
    ("Scheduling a viewing", "Scheduling a viewing"),
    ("Getting more information", "Getting more information"),
    ("Submitting an application", "Submitting an application"),
)


class ContactAgent(forms.ModelForm):
    schedule_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={"type": "date", "min": date.today().isoformat()}),
    )

    subject = forms.Select(choices=Schedule_TYPE)
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "Additional questions or preferred viewing times...",
                "rows": 4,
            }
        ),
    )

    class Meta:
        model = Schedule
        fields = ["schedule_date", "subject", "message"]

    def __init__(self, *args, user=None, **kwargs):
        super(ContactAgent, self).__init__(*args, **kwargs)
        if user:
            get_user = User.objects.get(username=user.username)
            if get_user.phone == None:
                self.fields["phone"] = PhoneNumberField(required=True)
                self.fields["phone"].widget.attrs["placeholder"] = "+20xxxxxxxxxx"
                self.fields["phone"].widget.attrs["class"] = "form-control"
                self.order_fields(
                    field_order=["phone", "schedule_date", "subject", "message"]
                )

        self.fields["subject"].widget.attrs["class"] = "form-control"
        self.fields["schedule_date"].widget.attrs["class"] = "form-control"
        self.fields["schedule_date"].help_text = "Make Sure Your Date is in Future"

    def clean_schedule_date(self):
        schedule_date = self.cleaned_data["schedule_date"]
        if schedule_date < timezone.now().date():
            raise forms.ValidationError("The Date is in Past.")
        return schedule_date


class ContactForProperty(forms.Form):
    username = forms.CharField(widget=forms.TextInput())
    email = forms.EmailField(widget=forms.EmailInput())
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "placeholder": "Tell us about your property or questions...",
                "rows": 4,
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super(ContactForProperty, self).__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["placeholder"] = "Username"
        self.fields["email"].widget.attrs["placeholder"] = "Email Address"
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"
            self.fields[field].required = True


class PhoneForm(forms.ModelForm):
    phone = PhoneNumberField(required=True)

    class Meta:
        model = User
        fields = ("phone",)

    def __init__(self, *args, **kwargs):
        super(PhoneForm, self).__init__(*args, **kwargs)
        self.fields["phone"].widget.attrs["placeholder"] = "+20xxxxxxxxxx"
        self.fields["phone"].widget.attrs["class"] = "form-control"


class PropertyForm(forms.ModelForm):
    available_at = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", min: date.today().isoformat()})
    )

    class Meta:
        model = Property
        fields = [
            "name",
            "main_image",
            "address",
            "rent",
            "price",
            "security_deposit",
            "bathrooms",
            "bedrooms",
            "meter",
            "interior_features",
            "building_amenities",
            "description",
            "category",
            "available_at",
        ]

    def __init__(self, *args, **kwargs):
        super(PropertyForm, self).__init__(*args, **kwargs)
        self.fields["available_at"].widget.attrs["placeholder"] = "YY-MM-DD"
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"
            self.fields[field].widget.attrs["placeholder"] = field.capitalize().replace(
                "_", " "
            )

    def clean_available_at(self):
        available_at = self.cleaned_data["available_at"]
        if available_at:
            if available_at < timezone.now().date():
                raise forms.ValidationError("The Date is in Past")
            return available_at
