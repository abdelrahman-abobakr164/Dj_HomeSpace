from .models import Category, Schedule
from datetime import date

def categoryfilter(request):
    categories = Category.objects.all()
    DatesCount = (
        Schedule.objects.filter(receiver=request.user, schedule_date__gte=date.today()).count()
        if request.user.is_authenticated
        else 0
    )
    return {
        "DatesCount": DatesCount,
        "categories": categories,
    }
