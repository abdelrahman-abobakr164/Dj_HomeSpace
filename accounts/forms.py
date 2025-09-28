from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSettings(forms.ModelForm):
    image = forms.ImageField(required=True, widget=forms.FileInput(attrs={'class':'form-control'}))
    class Meta:
        model = User
        fields = ["image", "username", "phone"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"
