from django.db import models
from django.contrib.auth.models import User
import os
from django.conf import settings



class Attribute(models.Model):
    name        = models.CharField(max_length=100)
    category    = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Badge(models.Model):
    name        = models.CharField(max_length=100)
    category    = models.CharField(max_length=100)
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
    
    def expanded_attributes(self):
        # 1) baseline 25 for every attribute
        attrs = {a.name: 25 for a in Attribute.objects.all()}
        # 2) enforce user‐selected badge minima
        for lvl in self.selected_levels.all():
            nm, mv = lvl.attribute.name, lvl.min_value
            attrs[nm] = max(attrs[nm], mv)

        # 3) apply each dependency rule by “obs_dep – (99 – your_value)”
        # only use deps for this exact height
        for dep in AttributeDependency.objects.filter(height=self.height):
            s     = attrs[dep.source.name]
            delta = dep.obs_source_value - s
            forced = dep.obs_dependent - delta
            # clamp to at least 25
            forced = max(forced, 25)
            # only raise if higher than current
            if forced > attrs[dep.dependent.name]:
                attrs[dep.dependent.name] = forced


        return attrs
    
    def compute_overall(self):
        """
        Estimate OVR by:
          1) summing the cost of every point from 25→final value,
          2) comparing against the cost from 25→99 for all attributes,
          3) scaling that fraction into the [25,99] range.
        """
        # 1) Build the height string (e.g. "7'3")
        feet, inches = divmod(self.height, 12)
        ht_str = f"{feet}'{inches}"

        # 2) Load all weights for this height into a dict for O(1) lookups
        aw_qs = {
            aw.attribute.name: aw
            for aw in AttributeWeight.objects.filter(height=ht_str)
        }

        # 3) Helper: cost to raise one attribute from 25→val
        def weight_sum(attr_name, val):
            aw = aw_qs.get(attr_name)
            if not aw or val <= 25:
                return 0.0
            total = 0.0
            brackets = [
                (25, 74, 'w_25_74'),
                (75, 79, 'w_75_79'),
                (80, 84, 'w_80_84'),
                (85, 89, 'w_85_89'),
                (90, 94, 'w_90_94'),
                (95, 98, 'w_95_98'),
                (99, 99, 'w_99'),
            ]
            for low, high, field in brackets:
                if val > low:
                    pts = min(val, high) - low
                    total += getattr(aw, field) * pts
            return total

        # 4) Compute raw_sum for your build’s finalized attributes
        final_attrs = self.expanded_attributes()  # {name: value}
        raw_sum = sum(weight_sum(name, value)
                      for name, value in final_attrs.items())

        # 5) Compute max_sum = cost to go 25→99 on *every* attribute
        max_sum = sum(weight_sum(name, 99) for name in aw_qs.keys())

        # 6) Avoid divide‐by‐zero, then scale into [25,99]
        if max_sum <= 0:
            return 25
        fraction = raw_sum / max_sum
        ovr = 25 + fraction * (99 - 25)
        return int(round(ovr))

    def __str__(self):
        return self.name

class AttributeWeight(models.Model):
    category     = models.CharField(max_length=50)
    height       = models.CharField(max_length=10)   # e.g. "7'3"
    attribute    = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    w_25_74      = models.FloatField()
    w_75_79      = models.FloatField()
    w_80_84      = models.FloatField()
    w_85_89      = models.FloatField()
    w_90_94      = models.FloatField()
    w_95_98      = models.FloatField()
    w_99         = models.FloatField()

    def __str__(self):
        return f"{self.height} – {self.attribute.name}"
    
class AttributeDependency(models.Model):
    height           = models.PositiveIntegerField(help_text="Player height in inches (e.g. 87 for 7'3\")")
    source            = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='deps_as_source')
    dependent         = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='deps_as_dependent')
    obs_source_value  = models.IntegerField(help_text="Observed source value at this height")
    obs_dependent     = models.IntegerField(help_text="Observed dependent value at this height")

    def __str__(self):
        return f"{self.source.name}@{self.obs_source_value} → {self.dependent.name}@{self.obs_dependent}"
    
def load_attribute_dependencies():
    """
    Read attribute-dependencies.csv (with columns:
      source-attribute, source-at-max,
      dependent-attribute, dependent-value,
      height-inches)
    and populate AttributeDependency.
    """
    AttributeDependency.objects.all().delete()
    path = os.path.join(settings.BASE_DIR, 'attribute-dependencies.csv')
    with open(path, 'r') as f:
        next(f)  # skip header
        for line in f:
            parts = [c.strip() for c in line.split(',')]
            # we need exactly 5 columns
            if len(parts) != 5:
                print(f"Skipping malformed: {line.strip()}")
                continue

            src, src_max, dep, dep_val, h = parts
            try:
                height_in      = int(h)
                source_attr    = Attribute.objects.get(name=src)
                dependent_attr = Attribute.objects.get(name=dep)
                src_max_i      = int(src_max)
                dep_val_i      = int(dep_val)
            except (ValueError, Attribute.DoesNotExist):
                print(f"Skipping malformed or unknown: {line.strip()}")
                continue

            AttributeDependency.objects.create(
                height           = height_in,
                source           = source_attr,
                dependent        = dependent_attr,
                obs_source_value = src_max_i,
                obs_dependent    = dep_val_i
            )

    print("Loaded", AttributeDependency.objects.count(), "dependencies")


def load_attribute_weights():
    """
    Clears and reloads the AttributeWeight table from your CSV,
    treating missing weight entries as zero.
    """
    # 1) delete old records
    AttributeWeight.objects.all().delete()

    # 2) locate the CSV file in your project root
    filename = 'attribute-weights.csv'
    path = os.path.join(settings.BASE_DIR, filename)

    with open(path, 'r') as f:
        for line in f:
            parts = [x.strip() for x in line.split(',')]
            # skip blank or malformed lines
            if len(parts) < 10:
                continue
            # skip header row
            if parts[0] == 'Category' or parts[2] == 'Attribute':
                continue

            cat       = parts[0]
            ht        = parts[1]
            attr_name = parts[2]
            # parse weight columns, treat empty strings as 0.0
            raw_vals = parts[3:10]
            vals = []
            for val in raw_vals:
                if val == '' or val.upper() == 'N/A':
                    vals.append(0.0)
                else:
                    try:
                        vals.append(float(val))
                    except ValueError:
                        vals.append(0.0)

            w25_74, w75_79, w80_84, w85_89, w90_94, w95_98, w99 = vals

            # lookup attribute
            try:
                attr = Attribute.objects.get(name=attr_name)
            except Attribute.DoesNotExist:
                print(f"Skipping unknown attribute: {attr_name}")
                continue

            # create record
            aw = AttributeWeight(
                category  = cat,
                height    = ht,
                attribute = attr,
                w_25_74   = w25_74,
                w_75_79   = w75_79,
                w_80_84   = w80_84,
                w_85_89   = w85_89,
                w_90_94   = w90_94,
                w_95_98   = w95_98,
                w_99      = w99,
            )
            aw.save()
            print(f"Loaded weight: {aw}")

    print(f"Done. {AttributeWeight.objects.count()} weight records.")