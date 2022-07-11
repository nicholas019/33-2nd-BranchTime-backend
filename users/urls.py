from django.urls import path

from .views      import KakaoLoginView, ProfileUpdate, UserDetailView

urlpatterns = [
    path('/kakao', KakaoLoginView.as_view()),
    path('/mypage', UserDetailView.as_view()),
    path('/profileupdate', ProfileUpdate.as_view(), name="profileupdate")
]
