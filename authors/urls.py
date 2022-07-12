from django.urls import path

from authors.views import ProposalView, AuthorListView, AuthorDetailView

urlpatterns = [
    path("/<int:author_id>/propoasl", ProposalView.as_view()),
    path("/list", AuthorListView.as_view()),
    path("/<int:author_id>/detail", AuthorDetailView.as_view()),
]
