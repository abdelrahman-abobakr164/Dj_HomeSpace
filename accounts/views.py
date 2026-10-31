from django.db.models import Q
from django.conf import settings
from django.http import QueryDict
from django.utils import timezone
from django.db import transaction
from django.contrib import messages
from django.core.mail import send_mail
from core.tasks import sendemails_to_users
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
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

    base_qs = Schedule.objects.filter(
        receiver=request.user, status="Pending", schedule_date__gte=today
    )
    schedules = base_qs.select_related("properties")
    filter_by_dates = base_qs.values_list("schedule_date", flat=True).distinct()

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

    base_qs = Schedule.objects.filter(sender=request.user)
    schedules = base_qs.select_related("properties")
    filter_by_dates = base_qs.values_list("schedule_date", flat=True).distinct()

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


DECISIONS = {
    "Accept": "Accepted",
    "Refuse": "Refused",
}


@login_required
@require_POST
def date_dicision(request, action, schedule_id):
    new_status = DECISIONS.get(action)
    if new_status is None:
        messages.error(request, "Invalid action.")
        return redirect("scheduled-viewing")

    with transaction.atomic():
        schedule = get_object_or_404(
            Schedule.objects.select_for_update(of=("self",)).select_related(
                "sender",
                "receiver",
                "properties",
            ),
            id=schedule_id,
            receiver=request.user,
            status="Pending",
        )
        
        if schedule.schedule_date < timezone.localdate():
            messages.error(request, "This date has passed, it's too late.")
            return redirect("scheduled-viewing")

        schedule.status = new_status
        schedule.save(update_fields=["status"])

        subject = f"{schedule.subject} Is {new_status}"
        body = (
            f"Your {schedule.subject} For {schedule.properties.name} "
            f"On {schedule.schedule_date} Is {new_status}"
        )
        transaction.on_commit(
            lambda: sendemails_to_users.delay(
                subject,
                body,
                schedule.receiver.email,
                schedule.sender.email,
            )
        )

    messages.success(request, f"The schedule date is {new_status.lower()}.")
    return redirect("scheduled-viewing")
