from django.urls import path

from authors.views import ProposalView, AuthorListView, AuthorDetailView

urlpatterns = [
    path("/<int:author_id>/propoasl", ProposalView.as_view()),
    path("/", AuthorListView.as_view()),
    path("/detail/<int:author_id>", AuthorDetailView.as_view()),
]
