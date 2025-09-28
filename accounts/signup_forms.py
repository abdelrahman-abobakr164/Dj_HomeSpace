from allauth.account.forms import SignupForm
from django import forms
from phonenumber_field.formfields import PhoneNumberField


class CustomSignupForm(SignupForm):
    image = forms.ImageField(required=True)
    phone = PhoneNumberField(required=True, region="EG")

    def save(self, request):
        user = super().save(request)
        user.image = self.cleaned_data.get("image")
        user.phone = self.cleaned_data.get("phone")
        user.save()
        return user
