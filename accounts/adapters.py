from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        if sociallogin.account.provider == "google":
            extra_data = sociallogin.account.extra_data
            image = extra_data.get("picture")

            user = sociallogin.user
            user.image = image

    def save_user(self, request, sociallogin, form=None):
        if sociallogin.account.provider == "google":
            user = super().save_user(request, sociallogin, form)
            extra_data = sociallogin.account.extra_data
            image = extra_data.get("picture")

            user.image = image
            user.save()
            return user
