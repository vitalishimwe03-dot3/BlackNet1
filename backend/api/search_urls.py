from django.urls import path
from .search_views import GlobalSearchView

urlpatterns = [
    path("", GlobalSearchView.as_view(), name="global_search"),
]