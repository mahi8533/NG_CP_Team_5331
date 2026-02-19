from django.db import models
from django.contrib.auth.models import User


class CropRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="crop_records")
    crop_name = models.CharField(max_length=120)
    field_area_acres = models.DecimalField(max_digits=8, decimal_places=2)
    sowing_date = models.DateField()
    expected_harvest_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-sowing_date", "-created_at"]

    def __str__(self):
        return f"{self.crop_name} ({self.user.username})"
