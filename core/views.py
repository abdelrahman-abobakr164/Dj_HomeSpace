from django.shortcuts import render, redirect, get_object_or_404, Http404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.core.cache import cache
from django.db import transaction
from django.http import QueryDict
from django.conf import settings
from django.db.models import Q
from decimal import Decimal

from core.forms import *
from core.models import *
from core.tasks import sendemails_to_users
from django.contrib.auth import get_user_model

User = get_user_model()


def index(request):
    premium = Property.objects.filter(Q(meter__gte=5000)).select_related("category")[:1]
    rental = Property.objects.filter(Q(rent__gte=2000)).select_related("category")[:2]
    disproperties = Property.objects.filter(discount_price__gte=1000000).select_related(
        "category"
    )[:1]
    allproperties = Property.objects.filter(price__gte=100000).select_related(
        "category"
    )[:1]
    properties = Property.objects.all().select_related("category")

    context = {
        "rental": rental,
        "premium": premium,
        "disproperties": disproperties,
        "properties": allproperties,
        "ps": properties,
    }
    return render(request, "core/index.html", context)


def properties(request):
    all_properties = Property.objects.select_related("category")

    location = request.GET.get("location")
    property_type = request.GET.get("property_type")
    min_price_range = request.GET.get("min_price_range")
    max_price_range = request.GET.get("max_price_range")
    forwhat = request.GET.get("for")
    bedrooms = request.GET.get("bedrooms")
    bathrooms = request.GET.get("bathrooms")

    params = request.GET.copy()
    clean_params = QueryDict(mutable=True)

    for key, value in params.items():
        if value and value.strip():
            clean_params[key] = value

    if len(clean_params) != len(params):
        if clean_params:
            return redirect(f"{request.path}?{clean_params.urlencode()}")
        else:
            return redirect(request.path)

    if min_price_range:
        min_price_range = Decimal(min_price_range)

    if clean_params.get("max_price_range"):
        max_price_range = Decimal(max_price_range)

    if clean_params.get("bathrooms"):
        all_properties = all_properties.filter(Q(bathrooms=bathrooms)).select_related(
            "category"
        )

    if clean_params.get("for"):
        if forwhat == "for-sale":
            all_properties = all_properties.filter(
                Q(property_type="For Sale")
            ).select_related("category")
        elif forwhat == "for-rent":
            all_properties = all_properties.filter(
                Q(property_type="For Rent")
            ).select_related("category")
        else:
            all_properties = all_properties.filter(Q())

    if clean_params.get("bedrooms"):
        all_properties = all_properties.filter(Q(bedrooms=bedrooms)).select_related(
            "category"
        )

    if clean_params.get("property_type"):
        all_properties = all_properties.filter(
            Q(category__id=property_type)
        ).select_related("category")

    if clean_params.get("location"):
        all_properties = all_properties.filter(
            Q(address__icontains=location)
        ).select_related("category")

    if clean_params.get("min_price_range") or clean_params.get("max_price_range"):
        all_properties = all_properties.filter(
            Q(
                price__gte=(min_price_range if min_price_range else Q()),
                price__lte=(max_price_range if max_price_range else Q()),
            )
            | Q(
                rent__gte=(min_price_range if min_price_range else Q()),
                rent__lte=(max_price_range if max_price_range else Q()),
            )
        ).select_related("category")

    paginator = Paginator(all_properties, 1)

    get_page = request.GET.get("page")
    try:
        page_obj = paginator.get_page(get_page)
    except EmptyPage:
        raise Http404("This page does not exist.")
    except ZeroDivisionError:
        messages.info(request, "Property Not Found")
        return redirect("properties")

    current_page = page_obj.number
    total_pages = paginator.num_pages
    group_size = 3
    group_start = ((current_page - 1) // group_size) * group_size + 1
    group_end = min(group_start + group_size - 1, total_pages)
    custom_page_range = range(group_start, group_end + 1)
    custom_pagi = paginator.num_pages - 3

    context = {
        "all_properties": all_properties,
        "custom_pagi": custom_pagi,
        "group_end": group_end,
        "total_pages": total_pages,
        "page_obj": page_obj,
        "custom_page_range": custom_page_range,
    }
    return render(request, "core/properties.html", context)


def property_detail(request, id):
    cache_key = f"Property{id}"
    get_property = cache.get(cache_key)
    if not get_property:
        get_property = (
            Property.objects.select_related("agent")
            .prefetch_related("gallaries", "interior_features", "building_amenities")
            .get(id=id)
        )
        cache.set(cache_key, get_property, timeout=60 * 15)
    similar_properties = Property.objects.filter(
        Q(rent__lte=get_property.rent if get_property.rent else Q())
        | Q(price__lte=get_property.price if get_property.price else Q())
    ).exclude(id=get_property.id)

    context = {
        "p": get_property,
        "form": ContactAgent(
            user=request.user if request.user.is_authenticated else None
        ),
        "similar_properties": similar_properties,
    }

    return render(request, "core/property-details.html", context)


@login_required
def add_property(request, username):
    user = get_object_or_404(User, username=username)
    if request.user != user:
        raise PermissionDenied
    if not user.phone:
        phoneform = PhoneForm(
            request.POST if request.method == "POST" else None, instance=user
        )
        if request.method == "POST" and phoneform.is_valid():
            phoneform.save()
            return redirect("add-property", username=user.username)
        if request.method == "POST":
            messages.error(request, "Please Provide a valid phone number")
        return render(request, "core/add_phone.html", {"form": phoneform})

    if request.method == "POST":
        images = request.FILES.getlist("images")
        form = PropertyForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                with transaction.atomic():
                    form_save = form.save(commit=False)
                    form_save.agent = user
                    form_save.property_type = (
                        "For Rent" if form.cleaned_data["rent"] else "For Sale"
                    )
                    form_save.save()
                    if images:
                        property_image(request, images, form_save.id)
                messages.success(request, "Your Property has been listed successfully!")
            except Exception:
                messages.error(request, "Somthing Went Wrong. Please Try Again")
        else:
            messages.error(request, f"Please correct the errors in the form.")
    else:
        form = PropertyForm()
    context = {"get_property": None, "form": form}
    return render(request, "core/property_form.html", context)


@login_required
def property_update(request, id):
    get_property = get_object_or_404(
        Property.objects.prefetch_related("interior_features", "building_amenities"),
        id=id,
    )
    if request.user != get_property.agent:
        raise PermissionDenied
    if request.method == "POST":
        form = PropertyForm(request.POST, request.FILES, instance=get_property)
        images = request.FILES.getlist("images")

        if form.is_valid():
            try:
                with transaction.atomic():
                    form_save = form.save(commit=False)
                    form_save.property_type = (
                        "For Rent" if form.cleaned_data["rent"] else "For Sale"
                    )
                    form_save.save()
                    if images:
                        property_image(request, images, get_property.id)
                    messages.success(
                        request, "Your Property Has Been Updated Successfully"
                    )
                    return redirect("property", id=get_property.id)
            except Exception:
                messages.error(request, "Somthing Went Wrong. Please Try Again")

        else:
            messages.error(request, f"Please correct the errors in the form.")

    return render(
        request,
        "core/property_form.html",
        {"form": form, "get_property": get_property},
    )


def property_image(request, images, property_id):
    ALLOWED_EXTENSION = ["JPG", "jpg", "png", "PNG", "webp"]
    gallery_objects = []
    for file in images:
        file_name = str(file.name)
        file_extension = file_name.split(".")[-1] if "." in file_name else ""
        if file_extension not in ALLOWED_EXTENSION:
            messages.error(request, f"the file {file_extension} is not supported")
            return redirect("property_update", id=property_id.id)
        gallery_objects.append(Gallery(property=property_id, images=file))
    Gallery.objects.bulk_create(gallery_objects)


@login_required
def property_delete(request, id):
    get_property = get_object_or_404(Property, id=id)
    if request.user != get_property.agent:
        raise PermissionDenied
    get_property.delete()
    messages.success(request, "Your Property Has Been Deleted Successfully!")
    return redirect("properties")


def services(request):
    return render(request, "core/services.html")


def service_detail(request, slug):
    if slug == "Property-Sell" or slug == "Property-Rental":

        form = ContactForProperty()

        if request.method == "POST":
            form = ContactForProperty(request.POST)
            if request.path == "/service/Property-Rental/":
                subject = "Property-Rental"
            else:
                subject = "Property-Sell"

            if form.is_valid():
                sendemails_to_users.delay(
                    subject=f"{subject}",
                    message=f"From {request.POST['username']}: {request.POST['message']}",
                    from_email=request.POST["email"],
                    recipient_list=settings.EMAIL_HOST_USER,
                )

                messages.success(
                    request,
                    f"Thank You {request.POST['username']} For Contacting Us We Will Respond to you Soon In Shaa Allah.",
                )
                return redirect(request.META.get("HTTP_REFERER"))
            else:
                messages.error(request, f"Please correct the errors in the form.")
    else:
        messages.error(request, "Wrong Service.")
        return redirect("services")
    return render(request, "core/service-details.html", {"form": form})


@login_required
def contact_agent(request, id):
    pro = get_object_or_404(Property, id=id)
    user = get_object_or_404(User, username=request.user.username)
    url = request.META.get("HTTP_REFERER")

    if request.method == "POST":
        form = ContactAgent(
            request.POST, user=user if request.user.is_authenticated else None
        )
        if form.is_valid():
            try:
                with transaction.atomic():
                    phone = form.cleaned_data.get("phone")

                    if phone:
                        user.phone = phone
                        user.save()
                    save_form = form.save(commit=False)
                    save_form.sender = user
                    save_form.receiver = pro.agent
                    save_form.properties_id = pro.id
                    save_form.save()

                message = form.cleaned_data.get("message")
                subject = form.cleaned_data["subject"]
                transaction.on_commit(
                    lambda: sendemails_to_users.delay(
                        subject=subject,
                        message=f"{user} \n Wanna {subject} \n Send You a: \n {message}. \n For Your Property {url}",
                        from_email=user.email,
                        recipient_list=pro.agent.email,
                    )
                )

                messages.success(request, f"Your Message Has been Sent Successfully!")
            except Exception:
                messages.error(request, "Somthing Went Wrong Please Try Again.")
        else:
            messages.error(request, "Please correct the errors in the form")
        return redirect(url)

    else:
        messages.error(request, f"Wrong Method.")
        return redirect(url)


def privacy(request):
    return render(request, "privacy.html")


def terms(request):
    return render(request, "terms.html")


def handler_404(request, exception):
    return render(request, "404.html", status=404)


def handler_500(request):
    return render(request, "500.html", status=500)
