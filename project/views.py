from itertools import groupby
import json
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView, FormView, TemplateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from .forms import BuildEditForm
from itertools import groupby
from django.utils.html import mark_safe
from .models import *
from .forms import *

def home(request):
    # temporary stub—just returns plain text
    render(request, 'project/home.html')

# 1. Listings & details

class AttributeListView(ListView):
    model = Attribute
    template_name = 'project/attribute_list.html'
    context_object_name = 'attributes'

class AttributeDetailView(DetailView):
    model = Attribute
    template_name = 'project/attribute_detail.html'
    context_object_name = 'attribute'


class BadgeListView(ListView):
    model               = Badge
    template_name       = 'project/badge_list.html'
    context_object_name = 'badges'

    def get_queryset(self):
        qs = super().get_queryset()

        # --- Category filter ---
        cat = self.request.GET.get('category', '').strip()
        if cat:
            qs = qs.filter(category=cat)

        # --- Height filter ---
        ht = self.request.GET.get('height', '').strip()
        if ht:
            try:
                ht_int = int(ht)
                qs = qs.filter(
                    levels__min_height__lte=ht_int,
                    levels__max_height__gte=ht_int
                )
            except ValueError:
                pass

        # --- Attribute filter ---
        raw_attrs = self.request.GET.getlist('attribute')
        attrs = [a for a in raw_attrs if a.strip()]
        if attrs:
            qs = qs.filter(levels__attribute__name__in=attrs)

        return qs.distinct()

    def get_context_data(self, **ctx):
        data = super().get_context_data(**ctx)

        # for the dropdowns
        data['all_categories'] = (
            Badge.objects
                 .values_list('category', flat=True)
                 .distinct()
                 .order_by('category')
        )
        data['all_heights'] = [(i, f"{i//12}'{i%12:02d}") for i in range(69, 88)]
        data['all_attributes'] = (
            Attribute.objects
                     .values_list('name', flat=True)
                     .distinct()
                     .order_by('name')
        )

        # re-derive exactly what the user typed
        selected_height = self.request.GET.get('height', '').strip()
        raw_attrs       = self.request.GET.getlist('attribute')
        selected_attrs  = [a for a in raw_attrs if a.strip()]

        data['selected_height']     = selected_height
        data['selected_attributes'] = selected_attrs

        return data


class BadgeDetailView(DetailView):
    model = Badge
    template_name = 'project/badge_detail.html'
    context_object_name = 'badge'

    def get_context_data(self, **kwargs):
        ctx   = super().get_context_data(**kwargs)
        badge = self.object

        levels = {}
        for code, label in BadgeLevel.LEVEL_CHOICES:
            reqs = badge.levels.filter(level=code)
            if not reqs.exists():
                continue

            # extract height range from the first row (they should all match)
            first = reqs.first()
            min_h, max_h = first.min_height, first.max_height
            # format as feet and inches
            min_h_str = f"{min_h//12}'{min_h%12}\""
            max_h_str = f"{max_h//12}'{max_h%12}\""
            height_range = f"{min_h_str} – {max_h_str}"

            # AND-requirements
            and_reqs = reqs.filter(alternative_group__isnull=True)

            # OR-groups
            or_reqs = []
            groups = (
                reqs.exclude(alternative_group__isnull=True)
                    .values_list('alternative_group', flat=True)
                    .distinct()
            )
            for grp in groups:
                or_reqs.append(reqs.filter(alternative_group=grp))

            levels[code] = {
                'label':        label,
                'height_range': height_range,
                'ands':         and_reqs,
                'ors':          or_reqs,
            }

        ctx['levels'] = levels
        return ctx



class BadgeLevelListView(ListView):
    model = BadgeLevel
    template_name = 'project/badgelevel_list.html'
    context_object_name = 'levels'

class BadgeLevelDetailView(DetailView):
    model = BadgeLevel
    template_name = 'project/badgelevel_detail.html'
    context_object_name = 'level'


class BuildListView(ListView):
    model = Build
    template_name = 'project/build_list.html'
    context_object_name = 'builds'

class BuildDetailView(DetailView):
    model               = Build
    template_name       = 'project/build_detail.html'
    context_object_name = 'build'

    def get_context_data(self, **kwargs):
        ctx   = super().get_context_data(**kwargs)
        build = self.object

        # Compute final attributes after dependencies
        final_attrs = build.expanded_attributes()

        # Which badges the user explicitly chose
        chosen = sorted({
            (lvl.badge.name, lvl.level)
            for lvl in build.selected_levels.select_related('badge')
        })

        # Find *all* badge‐levels they now satisfy by attribute:
        qs = BadgeLevel.objects.filter(
            min_height__lte=build.height,
            max_height__gte=build.height
        ).select_related('badge','attribute') \
         .order_by('badge__name','level','alternative_group')

        qualified = set()
        for (badge_name, level_code), rows in groupby(
                qs, key=lambda bl: (bl.badge.name, bl.level)
        ):
            if badge_name in {b for b,_ in chosen}:
                continue

            group_rows = list(rows)
            # AND‐requirements
            and_reqs = [r for r in group_rows if r.alternative_group is None]
            if not all(final_attrs[r.attribute.name] >= r.min_value for r in and_reqs):
                continue

            # OR‐requirements
            ok = True
            or_groups = {r.alternative_group for r in group_rows if r.alternative_group}
            for grp in or_groups:
                grp_rows = [r for r in group_rows if r.alternative_group == grp]
                if not any(final_attrs[r.attribute.name] >= r.min_value
                           for r in grp_rows):
                    ok = False
                    break
            if not ok:
                continue

            qualified.add((badge_name, level_code))

        # Reduce to highest‐level per badge:
        order = {'Bronze':1,'Silver':2,'Gold':3,'HoF':4,'Legend':5}
        best = {}
        for name,lvl in qualified:
            if name not in best or order[lvl] > order[best[name]]:
                best[name] = lvl
        extra = sorted(best.items())

        # # Attributes raised above 25
        # raised = sorted(
        #     [(n,v) for n,v in final_attrs.items() if v>25],
        #     key=lambda x: x[0]
        # )

        # show *all* attributes in your chosen NBA2K order ---
        desired_order = [
          "Close Shot","Driving Layup","Driving Dunk","Standing Dunk","Post Control",
          "Mid-Range Shot","Three-Point Shot","Free Throw",
          "Pass Accuracy","Ball Handle","Speed With Ball",
          "Interior Defense","Perimeter Defense","Steal","Block",
          "Offensive Rebound","Defensive Rebound","Speed","Agility","Strength","Vertical"
        ]
        all_attrs = [(name, final_attrs[name]) for name in desired_order]

        # now also push JSON arrays for *all* attributes
        names      = [n for n, _ in all_attrs]
        values     = [v for _, v in all_attrs]
        categories = [ Attribute.objects.get(name=n).category for n in names ]

        ctx.update({
            'chosen_badges':    chosen,
            'extra_badges':     extra,
            'raised_attrs':     [(n,v) for n,v in all_attrs if v>25],
            'attr_names_json':  mark_safe(json.dumps(names)),
            'attr_values_json': mark_safe(json.dumps(values)),
            'attr_cats_json':   mark_safe(json.dumps(categories)),
        })
        return ctx


# 2. New-build form

class BuildIntroView(FormView):
    template_name = 'project/build_intro.html'
    form_class    = BuildIntroForm

    def form_valid(self, form):
        build = Build.objects.create(
            name=form.cleaned_data['name'],
            height=form.cleaned_data['height'],
            user=self.request.user if self.request.user.is_authenticated else None
        )
        # stash the build’s PK in session for the next steps
        self.request.session['build_pk'] = build.pk
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('build_add_badge')
    
class BuildAddBadgeView(FormView):
    template_name = 'project/build_add_badge.html'
    form_class    = BadgeSelectionForm

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['build_pk'] = self.request.session.get('build_pk')
        return kw

    def dispatch(self, request, *args, **kwargs):
        if 'build_pk' not in request.session:
            return redirect('build_intro')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        build = get_object_or_404(Build, pk=self.request.session['build_pk'])

        # store any OR‐groups we need to resolve
        pending = {}

        # iterate each badge field
        for badge in Badge.objects.order_by('category','name'):
            lvl_code = form.cleaned_data.get(f'badge_{badge.pk}')
            if not lvl_code:
                continue

            # AND requirements
            and_qs = BadgeLevel.objects.filter(
                badge=badge, level=lvl_code, alternative_group__isnull=True
            )
            build.selected_levels.add(*and_qs)

            # collect OR‐groups
            rows = BadgeLevel.objects.filter(badge=badge, level=lvl_code).exclude(alternative_group__isnull=True)
            for grp in rows.values_list('alternative_group', flat=True).distinct():
                pending.setdefault(str(grp), []).extend(
                    rows.filter(alternative_group=grp).values_list('pk', flat=True)
                )

        build.save()

        if pending:
            self.request.session['pending_or'] = pending
            return redirect('build_resolve_or')

        return redirect('build_summary')

    def get_context_data(self, **kwargs):
        ctx  = super().get_context_data(**kwargs)
        form = ctx['form']

        # group the form fields by badge category
        grouped = {}
        for badge in Badge.objects.order_by('category','name'):
            cat   = badge.category
            field = form[f'badge_{badge.pk}']
            grouped.setdefault(cat, []).append(field)

        ctx['grouped_badges'] = grouped
        return ctx

    
class BuildResolveORView(FormView):
    template_name = 'project/build_resolve_or.html'
    form_class    = ResolveORForm

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('pending_or'):
            return redirect('build_add_badge')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['pending'] = self.request.session['pending_or']
        return kw

    def form_valid(self, form):
        build = get_object_or_404(Build, pk=self.request.session['build_pk'])
        chosen = []
        for name, val in form.cleaned_data.items():
            if name.startswith('group_'):
                chosen.append(int(val))
        build.selected_levels.add(*chosen)
        build.save()
        # clear pending
        del self.request.session['pending_or']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('build_summary')

class BuildSummaryView(TemplateView):
    template_name = 'project/build_summary.html'

    def get_context_data(self, **kwargs):
        ctx   = super().get_context_data(**kwargs)
        build = get_object_or_404(Build, pk=self.request.session['build_pk'])

        # compute your final expanded attributes
        final_attrs = build.expanded_attributes()

        # which badges the user explicitly chose
        chosen_badge_names = {
            lvl.badge.name
            for lvl in build.selected_levels.select_related('badge')
        }

        # figure out all the extra badges you now qualify for
        qualified = set()
        qs = BadgeLevel.objects.filter(
            min_height__lte=build.height,
            max_height__gte=build.height
        ).select_related('badge', 'attribute')
        qs = qs.order_by('badge__name', 'level', 'alternative_group')
        for (badge_name, level_code), group in groupby(
            qs, key=lambda bl: (bl.badge.name, bl.level)
        ):
            if badge_name in chosen_badge_names:
                continue

            rows = list(group)
            # AND requirements
            if not all(final_attrs[r.attribute.name] >= r.min_value
                       for r in rows if r.alternative_group is None):
                continue

            # OR requirements
            ok_or = True
            for grp in {r.alternative_group for r in rows if r.alternative_group}:
                grp_rows = [r for r in rows if r.alternative_group == grp]
                if not any(final_attrs[r.attribute.name] >= r.min_value
                           for r in grp_rows):
                    ok_or = False
                    break
            if not ok_or:
                continue

            qualified.add((badge_name, level_code))

        # pick highest‐level per badge
        level_order = {'Bronze':1,'Silver':2,'Gold':3,'HoF':4,'Legend':5}
        best = {}
        for badge_name, lvl in qualified:
            if (badge_name not in best or
                level_order[lvl] > level_order[best[badge_name]]):
                best[badge_name] = lvl
        extra = sorted(best.items())

        # chosen badges (one entry each)
        chosen = sorted({
            (lvl.badge.name, lvl.level)
            for lvl in build.selected_levels.select_related('badge')
        })

        # ─── NBA2K ATTRIBUTE ORDER ────────────────────────────────
        attr_order = [
          'Close Shot', 'Driving Layup', 'Driving Dunk', 'Standing Dunk',
          'Post Control', 'Mid-Range Shot', 'Three-Point Shot', 'Free Throw',
          'Pass Accuracy', 'Ball Handle', 'Speed With Ball',
          'Interior Defense', 'Perimeter Defense', 'Steal', 'Block',
          'Offensive Rebound', 'Defensive Rebound',
          'Speed', 'Agility', 'Strength', 'Vertical',
        ]

        # names in the exact order
        names = attr_order

        # look up each final value (25 if untouched)
        values = [ final_attrs.get(n, 25) for n in attr_order ]

        # category for each (for per-bar coloring)
        categories = [
          Attribute.objects.get(name=n).category
          for n in attr_order
        ]

        # dump to JSON and mark safe so Django won’t escape it
        ctx.update({
            'build':            build,
            'chosen_badges':    chosen,
            'extra_badges':     extra,
            # 'raised_attrs':     raised,
            'attr_names_json':  mark_safe(json.dumps(names)),
            'attr_values_json': mark_safe(json.dumps(values)),
            'attr_cats_json':   mark_safe(json.dumps(categories)),
        })
        return ctx

    
class BuildCreateView(FormView):
    template_name = 'project/build_form.html'
    form_class    = BuildForm
    success_url   = reverse_lazy('build_list')

    def get_context_data(self, **ctx):
        # First call super() so ctx is populated
        ctx = super().get_context_data(**ctx)

        # Grab the Build you’re editing
        build = get_object_or_404(Build, pk=self.request.session['build_pk'])

        # Re-create your attrs dict exactly as in BuildSummaryView
        attrs = {}
        for lvl in build.selected_levels.all():
            name = lvl.attribute.name
            # take the highest required value if multiple badge-levels touch the same attribute
            attrs[name] = max(attrs.get(name, 0), lvl.min_value)

        # Now you can safely assign
        ctx['build']             = build
        ctx['attributes']        = attrs.items()
        ctx['estimated_overall'] = build.compute_overall()
        return ctx

    def form_valid(self, form):
        # … your existing form processing …
        build = Build.objects.create(
            name = form.cleaned_data['name'],
            user = self.request.user if self.request.user.is_authenticated else None
        )
        build.selected_levels.set(form.selected_levels())
        return super().form_valid(form)


class BuildUpdateView(FormView):
    template_name = 'project/build_edit.html'
    form_class    = BuildEditForm

    def dispatch(self, request, *args, **kwargs):
        self.build = get_object_or_404(Build, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['instance'] = self.build
        if self.request.method in ('POST', 'PUT'):
            kw['data'] = self.request.POST
        return kw

    def get_context_data(self, **ctx):
        ctx = super().get_context_data(**ctx)
        # make build available in the template
        ctx['build'] = self.build
        return ctx

    def form_valid(self, form):
        form.save()
        return redirect('build_detail', self.build.pk)


class BuildDeleteView(DeleteView):
    model = Build
    template_name = 'project/build_confirm_delete.html'
    context_object_name = 'build'
    success_url = reverse_lazy('build_list')