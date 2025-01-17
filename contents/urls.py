from django.urls import path

from .views import CategoryView, PostListView, PostImageUpload, PostDetailView, PostUploadView, CommentUploadView, CommentUpdateView

urlpatterns = [
    path('/category', CategoryView.as_view()),
    path('/postlist', PostListView.as_view()),
    path('/postimageuploade', PostImageUpload.as_view()),
    path('/postupload', PostUploadView.as_view()),
    path('/post/<int:post_id>', PostDetailView.as_view()),
    path('/post/<int:post_id>/comment',CommentUploadView.as_view()),
    path('/post/<int:post_id>/comment/<int:comment_id>', CommentUpdateView.as_view()),
]
