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

    def get_context_data(self, **ctx):
        build = get_object_or_404(Build, pk=self.request.session['build_pk'])
        # aggregate attributes
        attrs = {}
        for lvl in build.selected_levels.all():
            key = lvl.attribute.name
            attrs[key] = max(attrs.get(key, 0), lvl.min_value)
        ctx.update({
            'build': build,
            'attributes': attrs.items(),
        })
        return ctx
    
class BuildCreateView(FormView):
    template_name = 'project/build_form.html'
    form_class    = BuildForm
    success_url   = reverse_lazy('build_list')

    def form_valid(self, form):
        # 1. Create the Build instance
        build = Build.objects.create(
            name = form.cleaned_data['name'],
            user = self.request.user if self.request.user.is_authenticated else None
        )

        # 2. Use the helper to get selected BadgeLevel objects
        build.selected_levels.set(form.selected_levels())

        return super().form_valid(form)

