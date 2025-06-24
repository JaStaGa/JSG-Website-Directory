from django import forms
from .models import AttributeCap, Badge, BadgeLevel, Build


class BuildIntroForm(forms.Form):
    name = forms.CharField(max_length=100, label="Build name")
    height = forms.ChoiceField(
        choices=[(i, f"{i//12}'{i%12:02d}") for i in range(69, 88)],
        label="Desired Height"
    )


# class SingleBadgeForm(forms.Form):
#     badge_level = forms.ChoiceField(label="Choose a Badge & Level")

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         pairs = (
#             (f"{b.id}|{lvl}", f"{b.name} — {label}")
#             for b in Badge.objects.all()
#             for lvl, label in BadgeLevel.LEVEL_CHOICES
#             if BadgeLevel.objects.filter(badge=b, level=lvl).exists()
#         )
#         self.fields['badge_level'].choices = [('', '— none —')] + sorted(pairs, key=lambda x: x[1])

class BadgeSelectionForm(forms.Form):
    """
    Renders one ChoiceField per Badge, letting the user pick
    None, Bronze, Silver, Gold, HoF or Legend—only for the levels
    that actually exist on that badge *and* that fit under your
    selected height’s attribute caps.
    """
    def __init__(self, *args, **kwargs):
        build_pk = kwargs.pop('build_pk', None)
        super().__init__(*args, **kwargs)

        # grab your caps for this height
        caps = {}
        if build_pk:
            build = Build.objects.get(pk=build_pk)
            for ac in AttributeCap.objects.filter(height=build.height):
                caps[ac.attribute_id] = ac.cap

        # now one field *per* badge
        for badge in Badge.objects.order_by('category','name'):
            field_name    = f'badge_{badge.pk}'
            level_choices = [('', '— none —')]
            for lvl_code, lvl_label in BadgeLevel.LEVEL_CHOICES:
                # only the rows valid at this height
                reqs = BadgeLevel.objects.filter(
                    badge=badge,
                    level=lvl_code,
                    min_height__lte=build.height,
                    max_height__gte=build.height,
                )
                if not reqs.exists():
                    continue

                # split AND vs OR
                invalid = False

                # AND rows
                for r in reqs.filter(alternative_group__isnull=True):
                    cap = caps.get(r.attribute_id, 99)
                    if r.min_value > cap:
                        invalid = True
                        break
                if invalid:
                    continue

                # OR groups
                or_groups = reqs.exclude(alternative_group__isnull=True) \
                                .values_list('alternative_group', flat=True) \
                                .distinct()
                for grp in or_groups:
                    group_rows = reqs.filter(alternative_group=grp)
                    if all(r.min_value > caps.get(r.attribute_id, 99)
                        for r in group_rows):
                        invalid = True
                        break
                if invalid:
                    continue

                level_choices.append((lvl_code, lvl_label))


            self.fields[field_name] = forms.ChoiceField(
                label=badge.name,
                choices=level_choices,
                required=False,
            )


class ResolveORForm(forms.Form):
    def __init__(self, *args, pending=None, **kwargs):
        super().__init__(*args, **kwargs)
        # pending is a dict: {grp: [pk1, pk2, …]}
        if pending:
            for grp, pending_pks in pending.items():
                levels = BadgeLevel.objects.filter(pk__in=pending_pks)
                choices = [
                    (level.pk, f"{level.attribute.name} ≥ {level.min_value}")
                    for level in levels
                ]
                self.fields[f'group_{grp}'] = forms.ChoiceField(
                    choices=choices,
                    widget=forms.RadioSelect,
                    label=f"Option for requirement group {grp}"
                )


class BuildForm(forms.Form):
    name = forms.CharField(max_length=100)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # For each badge, build a dropdown of its available levels
        for badge in Badge.objects.all():
            available = badge.levels.values_list('level', flat=True).distinct()
            choices = [('', '— none —')]
            for code, label in BadgeLevel.LEVEL_CHOICES:
                if code in available:
                    choices.append((code, label))
            self.fields[f'badge_{badge.id}'] = forms.ChoiceField(
                choices=choices,
                required=False,
                label=badge.name
            )

    def selected_levels(self):
        """
        Return a flat list of BadgeLevel instances corresponding
        to each badge+level the user chose.
        """
        levels = []
        for badge in Badge.objects.all():
            field_name = f'badge_{badge.id}'
            lvl_code = self.cleaned_data.get(field_name)
            if lvl_code:
                qs = BadgeLevel.objects.filter(badge=badge, level=lvl_code)
                levels.extend(list(qs))
        return levels

class BuildEditForm(forms.Form):
    name = forms.CharField(max_length=100, label="Build name")

    def __init__(self, *args, instance: Build, **kwargs):
        super().__init__(*args, **kwargs)
        self.build = instance

        # prefill the name
        self.fields['name'].initial = instance.name

        # for each badge, add a dropdown of its levels
        for badge in Badge.objects.all():
            # find which level‐codes exist for this badge
            available = (
                BadgeLevel.objects
                          .filter(badge=badge)
                          .values_list('level', flat=True)
                          .distinct()
            )
            # build choices list
            choices = [('', '— none —')]
            for code, label in BadgeLevel.LEVEL_CHOICES:
                if code in available:
                    choices.append((code, label))

            field_name = f'badge_{badge.id}'
            self.fields[field_name] = forms.ChoiceField(
                label=badge.name,
                choices=choices,
                required=False,
            )

            # if this build already had a level for that badge, pre‐select it
            sel = (
                instance.selected_levels
                        .filter(badge=badge)
                        .order_by('-level')  # pick highest if multiple
                        .first()
            )
            if sel:
                self.fields[field_name].initial = sel.level

    def save(self):
        # update the build’s name
        self.build.name = self.cleaned_data['name']
        self.build.save()

        # rebuild its selected_levels m2m
        picks = []
        for badge in Badge.objects.all():
            lvl_code = self.cleaned_data.get(f'badge_{badge.id}')
            if lvl_code:
                picks += list(BadgeLevel.objects.filter(badge=badge, level=lvl_code))
        self.build.selected_levels.set(picks)
        return self.build
