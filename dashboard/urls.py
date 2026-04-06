from django.urls import path
from .views import SummaryView, CategoryBreakdownView, RecentActivityView, MonthlyTrendView

urlpatterns = [
    path('summary/', SummaryView.as_view()),
    path('categories/', CategoryBreakdownView.as_view()),
    path('recent/', RecentActivityView.as_view()),
    path('trends/', MonthlyTrendView.as_view()),
]