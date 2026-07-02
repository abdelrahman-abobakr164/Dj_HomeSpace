from celery import shared_task
from django.conf import settings
from datetime import date
from django.core.mail import EmailMessage
from core.models import Property, Schedule


@shared_task
def update_property_availability():
    today = date.today()
    Property.objects.filter(available_at__lte=today, available=False).update(
        available=True
    )
    Property.objects.filter(available_at__gte=today, available=True).update(
        available=False
    )
    Schedule.objects.filter(schedule_date__lt=today, status="Pending").update(
        status="Refused"
    )


@shared_task
def sendemails_to_users(subject, message, from_email, recipient_list):
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.EMAIL_HOST_USER,
        to=[recipient_list],
        reply_to=[from_email],
    )
    email.send()
