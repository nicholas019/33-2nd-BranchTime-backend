from django.urls import path

from .views import CategoryView, PostListView, PostImageUpload, PostDetailView,CommentUploadView, PostUploadView, PostView, CommentView

urlpatterns = [
    path('/category', CategoryView.as_view()),
    path('/postlist', PostListView.as_view()),
    path('/postimageuploade', PostImageUpload.as_view()),
    path('/postupload', PostUploadView.as_view()),
    path('/post/<int:post_id>', PostDetailView.as_view()),
    path('/post/<int:post_id>/comment',CommentUploadView.as_view()),
    path("/comment/<int:comment_id>", CommentView.as_view()),
]
