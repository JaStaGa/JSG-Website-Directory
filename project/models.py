from django.db import models
from django.contrib.auth.models import User

class Attribute(models.Model):
    name        = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Badge(models.Model):
    name        = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class BadgeLevel(models.Model):
    LEVEL_CHOICES = [
        ('Bronze', 'Bronze'),
        ('Silver', 'Silver'),
        ('Gold', 'Gold'),
        ('HoF',    'Hall of Fame'),
        ('Legend','Legend'),
    ]

    badge             = models.ForeignKey(
                           Badge,
                           on_delete=models.CASCADE,
                           related_name='levels'
                         )
    level             = models.CharField(max_length=10, choices=LEVEL_CHOICES)
    attribute         = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    min_value         = models.PositiveIntegerField()
    alternative_group = models.PositiveIntegerField(null=True, blank=True,
                           help_text="Use same number for OR-requirements")
    min_height        = models.PositiveIntegerField(
                           default=69,
                           help_text="Player height in inches (5'9 = 69)"
                       )
    max_height        = models.PositiveIntegerField(
                           default=87,
                           help_text="Player height in inches (7'3 = 87)"
                       )

    class Meta:
        unique_together = ('badge', 'level', 'attribute', 'alternative_group')

    def __str__(self):
        return f"{self.badge.name} ({self.level}) → {self.attribute.name} ≥ {self.min_value}"


class Build(models.Model):
    name            = models.CharField(max_length=100)
    height             = models.PositiveIntegerField(null=True, blank=True, help_text="Player height in inches")
    selected_levels = models.ManyToManyField(BadgeLevel, blank=True)
    user            = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    @property
    def height_feet(self):
        return self.height // 12

    @property
    def height_inches(self):
        return self.height % 12

    def __str__(self):
        return self.name
