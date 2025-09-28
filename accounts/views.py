from django.db.models import Q
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail
from core.tasks import sendemails_to_users
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect


from core.models import Schedule
from accounts.models import Contact
from accounts.forms import UserSettings

User = get_user_model()


def contact_us(request):
    if request.method == "POST":
        email = request.POST.get("email")
        message = request.POST.get("message")
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


@login_required
def scheduled_viewing(request):
    today = timezone.now().date()
    schedules = Schedule.objects.filter(
        receiver=request.user, status="Pending", schedule_date__gte=today
    ).order_by("schedule_date")

    date = request.GET.get("date")
    status = request.GET.get("status")
    action = request.POST.get("action")
    schedule_id = request.POST.get("schedule")

    if request.method == "POST":
        try:
            schedule = get_object_or_404(Schedule, id=schedule_id, status="Pending")
            if schedule.schedule_date > today:
                if action == "Refuse":
                    schedule.status = "Refused"
                    schedule.save()
                    sendemails_to_users.delay(
                        f"{schedule.subject} Is Refused",
                        f"Your {schedule.subject} For {schedule.properties.name} On {schedule.schedule_date} Is Refused",
                        schedule.receiver.email,
                        schedule.sender.email,
                    )
                    messages.success(request, "The Schedule Date is Refused")
                elif action == "Accept":
                    schedule.status = "Accepted"
                    schedule.save()
                    sendemails_to_users.delay(
                        f"{schedule.subject} Is Accepted",
                        f"Your {schedule.subject} For {schedule.properties.name} On {schedule.schedule_date} Is Accepted",
                        schedule.receiver.email,
                        schedule.sender.email,
                    )
                    messages.success(request, "The Schedule Date is Accepted")
                else:
                    messages.error(request, "Don't Mess")
            else:
                messages.error(request, "The Date is Passed, It's Too Late")

        except Schedule.DoesNotExist:
            messages.error(request, "Don't Mess")

        return redirect("scheduled-viewing")

    if date:
        schedules = schedules.filter(Q(schedule_date=date))

    if status:
        schedules = schedules.filter(Q(status=status))

    context = {"schedules": schedules}
    return render(request, "accounts/scheduled_viewing.html", context)


@login_required
def dates(request):
    schedules = Schedule.objects.filter(sender=request.user).order_by("schedule_date")

    date = request.GET.get("date")
    status = request.GET.get("status")

    if date:
        schedules = schedules.filter(Q(schedule_date=date))

    if status:
        schedules = schedules.filter(Q(status=status))

    context = {"schedules": schedules}
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
            messages.error(request, f"{form.errors}")
    else:
        form = UserSettings(instance=user)
    return render(request, "accounts/my_account.html", {"profile": user, "form": form})
