from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Voter
from django.db.models import Q
from django.utils.timezone import now

def home(request):
    return render(request, 'directory/base.html')

# 8-2-1
class VoterListView(ListView):
    model = Voter
    template_name = 'voter_analytics/voter_list.html'
    context_object_name = 'voters'
    paginate_by = 100
    ordering = ['last_name', 'first_name']

    def get_queryset(self):
        queryset = Voter.objects.all()
        party = self.request.GET.get('party')
        min_dob = self.request.GET.get('min_dob')
        max_dob = self.request.GET.get('max_dob')
        score = self.request.GET.get('score')

        elections = ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']
        election_filters = {e: self.request.GET.get(e) == 'on' for e in elections}

        if party:
            queryset = queryset.filter(party_affiliation=party)

        if min_dob:
            queryset = queryset.filter(date_of_birth__year__gte=int(min_dob))

        if max_dob:
            queryset = queryset.filter(date_of_birth__year__lte=int(max_dob))

        if score:
            queryset = queryset.filter(voter_score=int(score))

        for election, voted in election_filters.items():
            if voted:
                queryset = queryset.filter(**{election: True})

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['parties'] = sorted(set(Voter.objects.values_list('party_affiliation', flat=True)))
        context['years'] = list(range(1900, now().year + 1))
        context['scores'] = sorted(set(Voter.objects.values_list('voter_score', flat=True)))
        context['filters'] = self.request.GET
        context['elections'] = ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']
        return context

# 8-2-3
class VoterDetailView(DetailView):
    model = Voter
    template_name = 'voter_analytics/voter_detail.html'
    context_object_name = 'voter'
