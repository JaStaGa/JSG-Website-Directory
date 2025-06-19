from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView, FormView, TemplateView
from django.urls import reverse_lazy, reverse

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
    model = Badge
    template_name = 'project/badge_list.html'
    context_object_name = 'badges'

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
    model = Build
    template_name = 'project/build_detail.html'
    context_object_name = 'build'


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
    form_class    = SingleBadgeForm

    def dispatch(self, request, *args, **kwargs):
        # ensure we have a build in session
        if 'build_pk' not in request.session:
            return redirect('build_intro')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        build = get_object_or_404(Build, pk=self.request.session['build_pk'])
        val   = form.cleaned_data['badge_level']
        if not val:
            return super().form_valid(form)  # nothing chosen
        badge_id, lvl = val.split('|')
        badge = Badge.objects.get(pk=badge_id)

        # gather the rows: AND requirements
        and_qs = BadgeLevel.objects.filter(badge=badge, level=lvl, alternative_group__isnull=True)

        # OR requirements grouped by group number
        or_groups = (
            (grp, list(BadgeLevel.objects.filter(
                badge=badge, level=lvl, alternative_group=grp
            )))
            for grp in BadgeLevel.objects
                        .filter(badge=badge, level=lvl)
                        .exclude(alternative_group__isnull=True)
                        .values_list('alternative_group', flat=True)
                        .distinct()
        )

        # if we have OR‐groups, save them in session to ask next
        self.request.session['pending_or'] = {
          str(grp): [lvl.pk for lvl in rows]
          for grp, rows in or_groups
        }
        # store the AND ones immediately
        build.selected_levels.add(*and_qs)
        build.save()

        # if any OR groups remain, branch to attribute choice
        if self.request.session['pending_or']:
            return redirect('build_choose_attr')

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('build_summary')
    
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

        final_attrs = build.expanded_attributes()

        # 1) which badges the user explicitly chose (any level)
        chosen_badge_names = {
            lvl.badge.name
            for lvl in build.selected_levels.select_related('badge')
        }

        # 2) collect all levels you now qualify for
        qualified = set()  # will hold (badge_name, level_code)
        qs = BadgeLevel.objects.filter(
            min_height__lte=build.height,
            max_height__gte=build.height
        ).select_related('badge', 'attribute')

        # group by badge+level
        from itertools import groupby
        # sort so groupby works
        qs = qs.order_by('badge__name', 'level', 'alternative_group')
        for (badge_name, level_code), group in groupby(
            qs, key=lambda bl: (bl.badge.name, bl.level)
        ):
            # skip badges the user already chose
            if badge_name in chosen_badge_names:
                continue

            rows = list(group)
            # AND requirements: those with no alt_group
            and_reqs = [r for r in rows if r.alternative_group is None]
            if not all(final_attrs[r.attribute.name] >= r.min_value
                       for r in and_reqs):
                continue

            # OR requirements: one pass in each alt_group
            ok_or = True
            or_groups = {r.alternative_group for r in rows
                         if r.alternative_group is not None}
            for grp in or_groups:
                grp_rows = [r for r in rows if r.alternative_group == grp]
                if not any(final_attrs[r.attribute.name] >= r.min_value
                           for r in grp_rows):
                    ok_or = False
                    break
            if not ok_or:
                continue

            # if we got here, you qualify for this badge+level
            qualified.add((badge_name, level_code))

        # 3) reduce to highest‐level per badge
        level_order = {'Bronze':1,'Silver':2,'Gold':3,'HoF':4,'Legend':5}
        best = {}
        for badge_name, lvl in qualified:
            if (badge_name not in best or
                level_order[lvl] > level_order[best[badge_name]]):
                best[badge_name] = lvl

        # 4) sort for display
        extra = sorted(best.items())

        # 5) chosen badges (show exactly what they picked)
        chosen = sorted(
            (lvl.badge.name, lvl.level)
            for lvl in build.selected_levels.select_related('badge')
        )

        # 6) attributes raised above 25
        raised = [(n, v) for n, v in final_attrs.items() if v > 25]

        ctx.update({
            'build':          build,
            'chosen_badges':  chosen,
            'extra_badges':   extra,
            'raised_attrs':   raised,
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


