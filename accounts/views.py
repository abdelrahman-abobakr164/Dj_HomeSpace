from django.db.models import Q
from django.conf import settings
from django.http import QueryDict
from django.utils import timezone
from django.db import transaction
from django.contrib import messages
from django.core.mail import send_mail
from core.tasks import sendemails_to_users
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404


from .utils import redirect_without_blank_params
from .forms import ScheduleFilterForm

from core.models import Schedule
from accounts.models import Contact
from accounts.forms import UserSettings

User = get_user_model()


@login_required
def scheduled_viewing(request):
    today = timezone.now().date()

    schedules = Schedule.objects.filter(
        receiver=request.user, status="Pending", schedule_date__gte=today
    ).select_related("properties")

    filter_by_dates = (
        Schedule.objects.filter(
            receiver=request.user, status="Pending", schedule_date__gte=today
        )
        .values_list("schedule_date", flat=True)
        .distinct()
    )

    form = ScheduleFilterForm(request.GET)
    if form.is_valid():
        if date := form.cleaned_data["date"]:
            schedules = schedules.filter(schedule_date=date)

    if request.method == "POST":
        date_dicision(request, request.POST.get("action"), request.POST.get("schedule"))

    context = {
        "filter_by_dates": filter_by_dates,
        "schedules": schedules,
    }
    return render(request, "accounts/scheduled_viewing.html", context)


@login_required
def dates(request):
    if response := redirect_without_blank_params(request):
        return response

    schedules = Schedule.objects.filter(sender=request.user).select_related(
        "properties"
    )

    filter_by_dates = (
        Schedule.objects.filter(sender=request.user)
        .values_list("schedule_date", flat=True)
        .distinct()
    )

    form = ScheduleFilterForm(request.GET)
    if form.is_valid():
        if date := form.cleaned_data["date"]:
            schedules = schedules.filter(Q(schedule_date=date))

        if status := form.cleaned_data["status"]:
            schedules = schedules.filter(Q(status=status))

    context = {
        "schedules": schedules,
        "filter_by_dates": filter_by_dates,
    }
    return render(request, "accounts/dates.html", context)


@login_required
def my_account(request):
    user = User.objects.get(username=request.user.username)
    if request.method == "POST":
        form = UserSettings(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("my-account")
        else:
            messages.error(request, f"Please correct the errors in the form.")
    else:
        form = UserSettings(instance=user)
    return render(request, "accounts/my_account.html", {"profile": user, "form": form})


def contact_us(request):
    if request.method == "POST":
        email = request.POST.get("email")
        message = request.POST.get("message")
        with transaction.atomic():
            Contact.objects.create(email=email, message=message)
            send_mail(
                subject="HomeSpace Contact-us",
                from_email=email,
                message=message,
                recipient_list=[settings.EMAIL_HOST_USER],
            )
        messages.success(
            request,
            f"Thank You For Contacting Us We Will Respond to you Very Soon In Shaa Allah.",
        )
        return redirect("contact-us")
    return render(request, "accounts/contact.html")


def date_dicision(request, action, schedule_id):
    today = timezone.now().date()
    schedule = get_object_or_404(Schedule, id=schedule_id, status="Pending")
    with transaction.atomic():
        if schedule.schedule_date >= today:
            if action == "Refuse":
                schedule.status = "Refused"
                schedule.save()
                transaction.on_commit(
                    lambda: sendemails_to_users.delay(
                        f"{schedule.subject} Is Refused",
                        f"Your {schedule.subject} For {schedule.properties.name} On {schedule.schedule_date} Is Refused",
                        schedule.receiver.email,
                        schedule.sender.email,
                    )
                )
                messages.success(request, "The Schedule Date is Refused")
            elif action == "Accept":
                schedule.status = "Accepted"
                schedule.save()
                transaction.on_commit(
                    lambda: sendemails_to_users.delay(
                        f"{schedule.subject} Is Accepted",
                        f"Your {schedule.subject} For {schedule.properties.name} On {schedule.schedule_date} Is Accepted",
                        schedule.receiver.email,
                        schedule.sender.email,
                    )
                )

                messages.success(request, "The Schedule Date is Accepted")
            else:
                messages.error(request, "Don't Mess")
        else:
            messages.error(request, "The Date is Passed, It's Too Late")

    return redirect("scheduled-viewing")
