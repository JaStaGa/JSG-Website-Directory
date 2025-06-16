from django import forms
from .models import Badge, BadgeLevel


class BuildIntroForm(forms.Form):
    name = forms.CharField(max_length=100, label="Build name")
    height = forms.ChoiceField(
        choices=[(i, f"{i//12}'{i%12:02d}") for i in range(69, 88)],
        label="Desired Height"
    )


class SingleBadgeForm(forms.Form):
    badge_level = forms.ChoiceField(label="Choose a Badge & Level")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pairs = (
            (f"{b.id}|{lvl}", f"{b.name} — {label}")
            for b in Badge.objects.all()
            for lvl, label in BadgeLevel.LEVEL_CHOICES
            if BadgeLevel.objects.filter(badge=b, level=lvl).exists()
        )
        self.fields['badge_level'].choices = [('', '— none —')] + sorted(pairs, key=lambda x: x[1])


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
