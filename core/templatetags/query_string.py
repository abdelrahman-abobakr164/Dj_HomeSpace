from django import template

register = template.Library()


@register.simple_tag
def query_string(request, **kwargs):
    income = request.GET.copy()
    for key in list(income.keys()):
        if not income[key]:
            del income[key]

    for key, value in kwargs.items():
        if value is not None and value != "":
            income[key] = str(value)
        else:
            income.pop(value, None)
    return income.urlencode()
