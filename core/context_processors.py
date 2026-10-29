from .models import Category, Schedule
from django.utils import timezone


def categoryfilter(request):
    categories = Category.objects.all()
    context = {"categories": categories}
    if request.user.is_authenticated:
        DatesCount = Schedule.objects.filter(
            receiver=request.user,
            status="Pending",
            schedule_date__gte=timezone.now().date(),
        ).count()
        context["DatesCount"] = DatesCount

    return context
