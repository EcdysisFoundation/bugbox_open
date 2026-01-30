from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from ..constants import (
    FIELD_CONDITION_CHOICES,
    SOIL_METRIC_CHOICES,
    TRANSECT_CODE_MAX_LENGTH,
    VEGETATION_METRIC_CHOICES,
)
from .application import GrowerApplication


class TransectMeasurement(models.Model):
    application = models.ForeignKey(
        GrowerApplication,
        on_delete=models.CASCADE,
        related_name='transect_measurements'
    )
    transect_index = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    transect_code = models.CharField(max_length=TRANSECT_CODE_MAX_LENGTH, blank=True)

    general_time = models.CharField(max_length=50, blank=True)
    temperature_c = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    wind_speed_ms = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    field_condition = models.CharField(max_length=20, choices=FIELD_CONDITION_CHOICES, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('application', 'transect_index')]
        ordering = ['application', 'transect_index']

    def __str__(self):
        return f"Measurement A:{self.application_id} T{self.transect_index} ({self.transect_code})"


class DropPlateReading(models.Model):
    measurement = models.ForeignKey(TransectMeasurement, on_delete=models.CASCADE, related_name='drop_plate')
    distance_m = models.IntegerField()
    value = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['distance_m']


class VegetationReading(models.Model):
    measurement = models.ForeignKey(TransectMeasurement, on_delete=models.CASCADE, related_name='vegetation')
    metric = models.CharField(max_length=50, choices=VEGETATION_METRIC_CHOICES)
    position_m = models.IntegerField()
    value = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['metric', 'position_m']


class SoilReading(models.Model):
    measurement = models.ForeignKey(TransectMeasurement, on_delete=models.CASCADE, related_name='soil')
    metric = models.CharField(max_length=50, choices=SOIL_METRIC_CHOICES)
    position_m = models.IntegerField()
    value = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['metric', 'position_m']


class SoilCompactionReading(models.Model):
    measurement = models.ForeignKey(TransectMeasurement, on_delete=models.CASCADE, related_name='compaction')
    position_m = models.IntegerField()
    max_value = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    score = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(2)])
    hp = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['position_m']


class InfiltrometerReading(models.Model):
    measurement = models.ForeignKey(TransectMeasurement, on_delete=models.CASCADE, related_name='infiltrometer')
    time_mark = models.CharField(max_length=10)
    volume_ml = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['time_mark']


class InfiltrationRingReading(models.Model):
    measurement = models.ForeignKey(TransectMeasurement, on_delete=models.CASCADE, related_name='infiltration_ring')
    pour_number = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(2)])
    start_depth_cm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    infiltration_time_sec = models.IntegerField(null=True, blank=True)
    depth_after_15min_cm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    change_in_depth_cm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['pour_number']

    def __str__(self):
        return f"Pour {self.pour_number}"
