from django.http import QueryDict
from django.shortcuts import redirect


def redirect_without_blank_params(request):
    cleaned = QueryDict(mutable=True)
    for key, values in request.GET.lists():
        for value in values:
            if value.strip():
                cleaned.appendlist(key, value)

    if cleaned.urlencode() == request.GET.urlencode():
        return None

    url = request.path
    if cleaned:
        url = f"{url}?{cleaned.urlencode()}"
    return redirect(url)
