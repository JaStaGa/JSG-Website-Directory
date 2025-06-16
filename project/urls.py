from django.urls import path
from .views import AttributeListView, AttributeDetailView, BadgeListView, BadgeDetailView, BadgeLevelListView, BadgeLevelDetailView, BuildListView, BuildDetailView, BuildIntroView, BuildAddBadgeView, BuildResolveORView, BuildSummaryView, home

urlpatterns = [
    path('', home, name='project_home'),

    path('attributes/',    AttributeListView .as_view(), name='attribute_list'),
    path('attributes/<int:pk>/', AttributeDetailView.as_view(), name='attribute_detail'),

    path('badges/',        BadgeListView.as_view(), name='badge_list'),
    path('badges/<int:pk>/', BadgeDetailView.as_view(), name='badge_detail'),

    path('levels/',        BadgeLevelListView.as_view(), name='badgelevel_list'),
    path('levels/<int:pk>/', BadgeLevelDetailView.as_view(), name='badgelevel_detail'),

    path('builds/',        BuildListView.as_view(), name='build_list'),
    path('builds/<int:pk>/', BuildDetailView.as_view(), name='build_detail'),

    path('builds/new/',        BuildIntroView.as_view(),       name='build_intro'),
    path('builds/new/badge/',  BuildAddBadgeView.as_view(),    name='build_add_badge'),
    path('builds/new/resolve/',BuildResolveORView.as_view(),   name='build_choose_attr'),
    path('builds/new/summary/',BuildSummaryView.as_view(),     name='build_summary'),

]