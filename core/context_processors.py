from .models import Category, Property


def categoryfilter(request):
    categories = Category.objects.all()
    return {
        "categories": categories,
    }
