import uuid
from django.db import models
from datetime import datetime
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator


User = get_user_model()


Schedule_TYPE = (
    ("Scheduling a viewing", "Scheduling a viewing"),
    ("Getting more information", "Getting more information"),
    ("Submitting an application", "Submitting an application"),
)

PROPERTY_FOR = (
    ("For Rent", "For Rent"),
    ("For Sale", "For Sale"),
)

PROPERTY_TYPE = (
    ("House", "House"),
    ("Apartment", "Apartment"),
    ("Villa", "Villa"),
    ("Compound", "Compound"),
)

Building_Amenities = (
    ("Rooftop terrace", "Rooftop terrace"),
    ("Fitness center", "Fitness center"),
    ("24/7 concierge", "24/7 concierge"),
    ("Indoor pool", "Indoor pool"),
)

Interior_Features = (
    ("Floor-to-ceiling windows", "Floor-to-ceiling windows"),
    ("Hardwood flooring", "Hardwood flooring"),
    ("Gourmet kitchen", "Gourmet kitchen"),
    ("In-unit washer/dryer", "In-unit washer/dryer"),
)


class Property(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True)
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="agents")
    main_image = models.FileField(upload_to="MainFile/")
    name = models.CharField(max_length=100)
    description = models.TextField()
    address = models.CharField(max_length=255)
    rent = models.DecimalField(
        decimal_places=0,
        max_digits=7,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
    )
    price = models.DecimalField(
        decimal_places=0,
        max_digits=7,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
    )
    discount_price = models.DecimalField(
        decimal_places=0,
        max_digits=7,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
    )
    security_deposit = models.DecimalField(
        decimal_places=0,
        max_digits=7,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
    )
    bathrooms = models.PositiveIntegerField()
    bedrooms = models.PositiveIntegerField()
    meter = models.DecimalField(
        decimal_places=0, max_digits=7, validators=[MinValueValidator(0)]
    )

    interior_features = models.ManyToManyField("InteriorFeatures", blank=True)
    building_amenities = models.ManyToManyField("BuildingAmenities", blank=True)
    category = models.ForeignKey(("Category"), on_delete=models.CASCADE)
    available_at = models.DateField(auto_now_add=False, blank=True, null=True)
    published_at = models.DateTimeField(auto_now_add=datetime.now())
    available = models.BooleanField(default=False)
    property_type = models.CharField(max_length=100, choices=PROPERTY_FOR)
    slug = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

    def discount_percentage(self):
        if self.discount_price and self.price:
            discount = ((self.price - self.discount_price) / self.price) * 100
            return f" %{round(discount, 1 )}"
        return 0

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-published_at"]
        verbose_name = "property"
        verbose_name_plural = "properties"


SCHEDULE_CHOICES = (
    ("Pending", "Pending"),
    ("Accepted", "Accepted"),
    ("Refused", "Refused"),
)


class Schedule(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="receiver"
    )
    properties = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name="schedules"
    )
    subject = models.CharField(max_length=100, choices=Schedule_TYPE)
    message = models.TextField(max_length=300, blank=True, null=False)
    status = models.CharField(
        max_length=50, choices=SCHEDULE_CHOICES, default="Pending"
    )
    schedule_date = models.DateField(auto_now_add=False)

    def __str__(self):
        return self.properties.name

    class Meta:
        ordering = ("-schedule_date",)
        verbose_name = "Schedule"
        verbose_name_plural = "Schedules"


class InteriorFeatures(models.Model):
    name = models.CharField(max_length=100, choices=Interior_Features)

    def __str__(self):
        return self.name


class BuildingAmenities(models.Model):
    name = models.CharField(max_length=100, choices=Building_Amenities)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, choices=PROPERTY_TYPE)

    def __str__(self):
        return self.name


class Gallary(models.Model):
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name="gallaries"
    )
    images = models.FileField(upload_to="Properites_Gallary/", null=True, blank=True)

    def __str__(self):
        return self.property.name
