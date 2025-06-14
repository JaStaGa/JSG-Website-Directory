from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView
from .models import Voter
from django.db.models import Q
from django.utils.timezone import now
from django.db.models.query import QuerySet
import plotly.graph_objs as go
from plotly.offline import plot
from django.db import models



def home(request):
    return render(request, 'directory/base.html')

def base(request):
    return render(request, 'voter_analytics/base.html')

# 8-2
class VoterListView(ListView):
    model = Voter
    template_name = 'voter_analytics/voter_list.html'
    context_object_name = 'voters'
    paginate_by = 100
    ordering = ['last_name', 'first_name']

    def get_queryset(self):
        voters = super().get_queryset()

        party = self.request.GET.get('party')
        if party:
            voters = voters.filter(party_affiliation=party)

        min_dob = self.request.GET.get('min_dob')
        if min_dob:
            voters = voters.filter(date_of_birth__year__gte=int(min_dob))

        max_dob = self.request.GET.get('max_dob')
        if max_dob:
            voters = voters.filter(date_of_birth__year__lte=int(max_dob))

        score = self.request.GET.get('score')
        if score:
            voters = voters.filter(voter_score=int(score))

        for election in ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']:
            if self.request.GET.get(election) == 'on':
                voters = voters.filter(**{election: 'TRUE'})

        return voters
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get info for filtering
        context['parties'] = sorted(set(Voter.objects.values_list('party_affiliation', flat=True)))
        context['years'] = sorted(set(v.date_of_birth.year for v in Voter.objects.all()))
        context['scores'] = sorted(set(Voter.objects.values_list('voter_score', flat=True)))
        context['elections'] = ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']
        context['filters'] = self.request.GET  # Pass current filters back to the template

        return context
    #     return voters[:25]
    #     queryset = Voter.objects.all()
    #     party = self.request.GET.get('party')
    #     min_dob = self.request.GET.get('min_dob')
    #     max_dob = self.request.GET.get('max_dob')
    #     score = self.request.GET.get('score')

    #     elections = ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']
    #     election_filters = {e: self.request.GET.get(e) == 'on' for e in elections}

    #     if party:
    #         queryset = queryset.filter(party_affiliation=party)

    #     if min_dob:
    #         queryset = queryset.filter(date_of_birth__year__gte=int(min_dob))

    #     if max_dob:
    #         queryset = queryset.filter(date_of_birth__year__lte=int(max_dob))

    #     if score:
    #         queryset = queryset.filter(voter_score=int(score))

    #     for election, voted in election_filters.items():
    #         if voted:
    #             queryset = queryset.filter(**{election: True})

    #     return queryset.distinct()

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['parties'] = sorted(set(Voter.objects.values_list('party_affiliation', flat=True)))
    #     context['years'] = list(range(1900, now().year + 1))
    #     context['scores'] = sorted(set(Voter.objects.values_list('voter_score', flat=True)))
    #     context['filters'] = self.request.GET
    #     context['elections'] = ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']
    #     return context

# 8-2
class VoterDetailView(DetailView):
    model = Voter
    template_name = 'voter_analytics/voter_detail.html'
    context_object_name = 'voter'

# 8-3
class VoterGraphView(TemplateView):
    template_name = 'voter_analytics/graphs.html'

    # filtering
    def get_filtered_queryset(self):
        voters = Voter.objects.all()
        request = self.request.GET

        party = request.get('party')
        if party:
            voters = voters.filter(party_affiliation=party)

        min_dob = request.get('min_dob')
        if min_dob:
            voters = voters.filter(date_of_birth__year__gte=int(min_dob))

        max_dob = request.get('max_dob')
        if max_dob:
            voters = voters.filter(date_of_birth__year__lte=int(max_dob))

        score = request.get('score')
        if score:
            voters = voters.filter(voter_score=int(score))

        for election in ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']:
            if request.get(election) == 'on':
                voters = voters.filter(**{election: '1'})  # or True if boolean

        return voters

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 1. Birth Year Histogram
        voters = self.get_filtered_queryset()
        birth_years = voters.values_list('date_of_birth', flat=True)
        year_counts = {}

        for dob in birth_years:
            if dob:  # skip nulls
                year = dob.year
                year_counts[year] = year_counts.get(year, 0) + 1

        birth_fig = go.Figure([
            go.Bar(x=list(year_counts.keys()), y=list(year_counts.values()))
        ])
        birth_fig.update_layout(
            title='Distribution of Voters by Birth Year',
            xaxis_title='Year of Birth',
            yaxis_title='Number of Voters'
        )
        context['birth_plot'] = plot(birth_fig, output_type='div')

        # 2. Party Affiliation Pie Chart
        party_counts = (
            voters.values('party_affiliation')
            .annotate(count=models.Count('id'))
            .order_by()
        )
        labels = [item['party_affiliation'].strip() for item in party_counts]
        values = [item['count'] for item in party_counts]

        party_fig = go.Figure([
            go.Pie(labels=labels, values=values)
        ])
        party_fig.update_layout(title='Party Affiliation Distribution')
        context['party_plot'] = plot(party_fig, output_type='div')

        # 3. Election Participation Histogram
        elections = ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']
        voted_counts = []

        for field in elections:
            count = voters.filter(**{field: 'TRUE'}).count()
            voted_counts.append(count)

        election_fig = go.Figure([
            go.Bar(x=elections, y=voted_counts)
        ])
        election_fig.update_layout(
            title='Participation in Each Election',
            xaxis_title='Election',
            yaxis_title='Number of Voters Who Participated'
        )
        context['election_plot'] = plot(election_fig, output_type='div')
        context['filters'] = self.request.GET
        context['parties'] = sorted(set(Voter.objects.values_list('party_affiliation', flat=True)))
        context['years'] = sorted(set(v.date_of_birth.year for v in Voter.objects.all()))
        context['scores'] = sorted(set(Voter.objects.values_list('voter_score', flat=True)))
        context['elections'] = ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']

        return context