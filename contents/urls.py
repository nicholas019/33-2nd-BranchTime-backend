from django.urls import path

from .views import CategoryView, CommentUploadView, PostUploadView, ContentImageUploadView, PostView, CommentView,PostListView

urlpatterns = [
    path('/category', CategoryView.as_view()),
    path("/<int:post_id>/comment", CommentUploadView.as_view()),
    path("/", PostUploadView.as_view()),
    path("/media", ContentImageUploadView.as_view()), 
    path("/<int:post_id>", PostView.as_view()),
    path("/commentupload/<int:comment_id>", CommentUploadView.as_view()),
    path("/<int:post_id>/comment", CommentUploadView.as_view()),
    path("/comment/<int:comment_id>", CommentView.as_view()),
    path("/postlist/<int:maincategory_id>", PostListView.as_view()),
]
