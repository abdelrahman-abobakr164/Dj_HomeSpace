from celery import shared_task
from django.utils import timezone
from core.models import Property, Schedule
from django.core.mail import send_mail


@shared_task
def update_property_availability():
    today = timezone.now().date()
    Property.objects.filter(available_at__lte=today, available=False).update(
        available=True
    )
    Property.objects.filter(available_at__gte=today, available=True).update(
        available=False
    )
    Schedule.objects.filter(schedule_date__gt=today, status="Pending").update(
        status="Refused"
    )

    return None


@shared_task
def sendemails_to_users(subject, message, from_email, recipient_list):
    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=[recipient_list],
        fail_silently=False,
    )

    return None
